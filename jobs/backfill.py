#!/usr/bin/env python3
"""
Network Efficiency ETL - Historical Data Backfill

This script performs a one-time backfill of the last 90 days of network efficiency
data from CSV source files and BigQuery tables. It processes historical meter data
to populate the sensor_readings table and materialized views.

Usage:
    python jobs/backfill.py [--days=90] [--start-date=YYYY-MM-DD] [--end-date=YYYY-MM-DD]
    
Examples:
    python jobs/backfill.py --days=90
    python jobs/backfill.py --start-date=2024-01-01 --end-date=2024-03-31
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from google.cloud import bigquery
import asyncpg
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.database.postgres_manager import get_postgres_manager
from src.infrastructure.bigquery.bigquery_client import BigQueryClient
from src.infrastructure.cache.redis_cache_manager import RedisCacheManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backfill.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# CSV source file locations
CSV_SOURCES = {
    'backup_data': project_root / "RAWDATA" / "NEW_DATA" / "BACKUP",
    'normalized_data': project_root / "normalized_data.csv",
    'cleaned_data': project_root / "cleaned_data.csv",
    'teatinos_data': project_root / "teatinos_hidroconta_normalized.csv",
    'quartucciu_data': project_root / "normalized_quartucciu.csv",
    'selargius_data': project_root / "normalized_selargius.csv"
}


class NetworkEfficiencyBackfill:
    """Backfill pipeline for network efficiency historical data."""
    
    def __init__(self, batch_size: int = 10000, max_workers: int = 4):
        """
        Initialize backfill pipeline.
        
        Args:
            batch_size: Number of records to process in each batch
            max_workers: Maximum concurrent workers for parallel processing
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.bigquery_client = BigQueryClient()
        self.postgres_manager = None
        self.redis_manager = RedisCacheManager()
        
        # Backfill statistics
        self.stats = {
            'total_records': 0,
            'processed_records': 0,
            'failed_records': 0,
            'nodes_processed': 0,
            'csv_files_processed': 0,
            'bigquery_tables_processed': 0,
            'start_time': None,
            'end_time': None,
            'date_range': None
        }
        
    async def initialize(self) -> None:
        """Initialize database connections."""
        self.postgres_manager = await get_postgres_manager()
        await self.redis_manager.initialize()
        logger.info("Network Efficiency Backfill initialized")
        
    async def backfill_data(
        self,
        start_date: datetime,
        end_date: datetime,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Backfill historical data for the specified date range.
        
        Args:
            start_date: Start date for backfill
            end_date: End date for backfill
            force_refresh: Force refresh even if data exists
            
        Returns:
            Backfill execution statistics
        """
        logger.info(f"Starting backfill from {start_date} to {end_date}")
        self.stats['start_time'] = datetime.now()
        self.stats['date_range'] = f"{start_date.date()} to {end_date.date()}"
        
        try:
            # Create ETL job record
            job_id = await self.postgres_manager.log_etl_job({
                'job_name': f'network_efficiency_backfill_{start_date.date()}_{end_date.date()}',
                'job_type': 'backfill',
                'status': 'running',
                'started_at': self.stats['start_time'],
                'metadata': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'force_refresh': force_refresh,
                    'batch_size': self.batch_size
                }
            })
            
            # Check if data already exists (unless force refresh)
            if not force_refresh:
                existing_count = await self._check_existing_data(start_date, end_date)
                if existing_count > 0:
                    logger.info(f"Found {existing_count} existing records in date range")
                    logger.info("Use --force-refresh to override existing data")
                    
            # Step 1: Backfill from BigQuery sources
            await self._backfill_from_bigquery(start_date, end_date)
            
            # Step 2: Backfill from CSV files
            await self._backfill_from_csv_files(start_date, end_date)
            
            # Step 3: Backfill from backup data
            await self._backfill_from_backup_data(start_date, end_date)
            
            # Step 4: Refresh materialized views
            await self._refresh_materialized_views()
            
            # Update job status
            self.stats['end_time'] = datetime.now()
            await self.postgres_manager.update_etl_job(job_id, {
                'status': 'completed',
                'completed_at': self.stats['end_time'],
                'records_processed': self.stats['processed_records'],
                'metadata': {
                    **self.stats,
                    'duration_seconds': (self.stats['end_time'] - self.stats['start_time']).total_seconds()
                }
            })
            
            logger.info(f"Backfill completed: {self.stats}")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Backfill failed: {e}")
            if 'job_id' in locals():
                await self.postgres_manager.update_etl_job(job_id, {
                    'status': 'failed',
                    'completed_at': datetime.now(),
                    'error_message': str(e)
                })
            raise
            
    async def _backfill_from_bigquery(self, start_date: datetime, end_date: datetime) -> None:
        """Backfill data from BigQuery sources."""
        logger.info("Backfilling from BigQuery sources")
        
        # List of BigQuery tables to process
        tables = [
            'sensor_readings_ml',
            'v_sensor_readings_normalized',
            'sensor_data',
            'teatinos_infrastructure.sensor_data',
            'quartucciu_infrastructure.sensor_data',
            'selargius_infrastructure.sensor_data'
        ]
        
        for table in tables:
            try:
                await self._backfill_from_bigquery_table(table, start_date, end_date)
                self.stats['bigquery_tables_processed'] += 1
                
            except Exception as e:
                logger.error(f"Error backfilling from BigQuery table {table}: {e}")
                self.stats['failed_records'] += 1
                
    async def _backfill_from_bigquery_table(
        self,
        table_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> None:
        """Backfill data from a specific BigQuery table."""
        logger.info(f"Processing BigQuery table: {table_name}")
        
        # Handle different table schemas
        if table_name == 'sensor_readings_ml':
            query = f"""
            SELECT 
                timestamp,
                node_id,
                node_name,
                temperature,
                flow_rate,
                pressure,
                volume as total_flow,
                data_quality_score as quality_score,
                district_id,
                district_name
            FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.{table_name}`
            WHERE timestamp BETWEEN @start_date AND @end_date
            AND data_quality_score > 0.3
            ORDER BY timestamp
            """
        elif table_name == 'v_sensor_readings_normalized':
            query = f"""
            SELECT 
                timestamp,
                node_id,
                node_name,
                temperature,
                flow_rate,
                pressure,
                volume as total_flow,
                1.0 as quality_score,
                'legacy' as district_id,
                'Legacy System' as district_name
            FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.{table_name}`
            WHERE timestamp BETWEEN @start_date AND @end_date
            ORDER BY timestamp
            """
        else:
            # Generic sensor_data table
            query = f"""
            SELECT 
                timestamp,
                node_id,
                '{table_name}' as node_name,
                temperature,
                flow_rate,
                pressure,
                volume as total_flow,
                0.8 as quality_score,
                SPLIT('{table_name}', '.')[0] as district_id,
                SPLIT('{table_name}', '.')[0] as district_name
            FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.{table_name}`
            WHERE timestamp BETWEEN @start_date AND @end_date
            AND flow_rate IS NOT NULL
            ORDER BY timestamp
            """
            
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
                bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date),
            ]
        )
        
        try:
            df = self.bigquery_client.client.query(query, job_config=job_config).to_dataframe()
            
            if not df.empty:
                await self._process_and_load_data(df, f'bigquery_{table_name}')
                logger.info(f"Processed {len(df)} records from BigQuery table {table_name}")
                
        except Exception as e:
            logger.error(f"Error querying BigQuery table {table_name}: {e}")
            
    async def _backfill_from_csv_files(self, start_date: datetime, end_date: datetime) -> None:
        """Backfill data from CSV files."""
        logger.info("Backfilling from CSV files")
        
        for source_name, file_path in CSV_SOURCES.items():
            if source_name == 'backup_data':
                continue  # Handle backup data separately
                
            try:
                if file_path.exists():
                    await self._process_csv_file(file_path, source_name, start_date, end_date)
                    self.stats['csv_files_processed'] += 1
                else:
                    logger.warning(f"CSV file not found: {file_path}")
                    
            except Exception as e:
                logger.error(f"Error processing CSV file {file_path}: {e}")
                self.stats['failed_records'] += 1
                
    async def _process_csv_file(
        self,
        file_path: Path,
        source_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> None:
        """Process a single CSV file."""
        logger.info(f"Processing CSV file: {file_path}")
        
        try:
            # Read CSV file in chunks
            chunk_size = self.batch_size
            
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                # Standardize column names
                chunk = self._standardize_csv_columns(chunk, source_name)
                
                # Filter by date range
                if 'timestamp' in chunk.columns:
                    chunk['timestamp'] = pd.to_datetime(chunk['timestamp'])
                    chunk = chunk[
                        (chunk['timestamp'] >= start_date) & 
                        (chunk['timestamp'] <= end_date)
                    ]
                    
                    if not chunk.empty:
                        await self._process_and_load_data(chunk, f'csv_{source_name}')
                        
        except Exception as e:
            logger.error(f"Error processing CSV file {file_path}: {e}")
            
    def _standardize_csv_columns(self, df: pd.DataFrame, source_name: str) -> pd.DataFrame:
        """Standardize CSV column names to match our schema."""
        column_mapping = {
            # Common mappings
            'data': 'date',
            'ora': 'time',
            'datetime': 'timestamp',
            'datetime_combined': 'timestamp',
            
            # Flow rate mappings
            'portata': 'flow_rate',
            'flow': 'flow_rate',
            'portata_w_istantanea_diretta': 'flow_rate',
            'metric_3': 'flow_rate',
            
            # Pressure mappings
            'pressione': 'pressure',
            'pressure_bar': 'pressure',
            
            # Temperature mappings
            'temperatura': 'temperature',
            'temperature_c': 'temperature',
            'temperatura_interna': 'temperature',
            
            # Volume mappings
            'volume': 'total_flow',
            'volume_m3': 'total_flow',
            
            # Node ID mappings
            'node': 'node_id',
            'sensor_id': 'node_id',
            'pcr_unit': 'node_id',
            '_pcr_unit': 'node_id'
        }
        
        # Apply column mappings
        df = df.rename(columns=column_mapping)
        
        # Create timestamp if we have separate date/time columns
        if 'date' in df.columns and 'time' in df.columns:
            df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'], errors='coerce')
            
        # Add missing columns with defaults
        if 'node_id' not in df.columns:
            df['node_id'] = f'{source_name}_node'
            
        if 'node_name' not in df.columns:
            df['node_name'] = f'{source_name.title()} Node'
            
        if 'quality_score' not in df.columns:
            df['quality_score'] = 0.7
            
        if 'district_id' not in df.columns:
            df['district_id'] = source_name
            
        if 'district_name' not in df.columns:
            df['district_name'] = source_name.title()
            
        return df
        
    async def _backfill_from_backup_data(self, start_date: datetime, end_date: datetime) -> None:
        """Backfill data from backup directory."""
        logger.info("Backfilling from backup data")
        
        backup_dir = CSV_SOURCES['backup_data']
        if not backup_dir.exists():
            logger.warning(f"Backup directory not found: {backup_dir}")
            return
            
        # Process backup files in parallel
        backup_files = list(backup_dir.glob("**/*.csv"))
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = []
            
            for file_path in backup_files:
                task = executor.submit(
                    self._process_backup_file_sync,
                    file_path,
                    start_date,
                    end_date
                )
                tasks.append(task)
                
            for task in tqdm(tasks, desc="Processing backup files"):
                try:
                    result = task.result()
                    if result:
                        await self._process_and_load_data(result, 'backup_data')
                        self.stats['csv_files_processed'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing backup file: {e}")
                    self.stats['failed_records'] += 1
                    
    def _process_backup_file_sync(
        self,
        file_path: Path,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """Process backup file synchronously (for thread pool)."""
        try:
            df = pd.read_csv(file_path)
            
            # Extract node ID from filename
            node_id = file_path.stem.split('_')[0]
            
            # Standardize columns
            df = self._standardize_csv_columns(df, f'backup_{node_id}')
            
            # Filter by date range
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df[
                    (df['timestamp'] >= start_date) & 
                    (df['timestamp'] <= end_date)
                ]
                
            return df if not df.empty else None
            
        except Exception as e:
            logger.error(f"Error processing backup file {file_path}: {e}")
            return None
            
    async def _process_and_load_data(self, df: pd.DataFrame, source: str) -> None:
        """Process and load data into PostgreSQL."""
        if df.empty:
            return
            
        # Ensure nodes exist
        unique_nodes = df['node_id'].unique()
        await self._ensure_nodes_exist(unique_nodes, df)
        
        # Process in batches
        for i in range(0, len(df), self.batch_size):
            batch_df = df.iloc[i:i + self.batch_size]
            
            # Convert to readings format
            readings = []
            for _, row in batch_df.iterrows():
                reading = {
                    'timestamp': row['timestamp'].to_pydatetime(),
                    'node_id': str(row['node_id']),
                    'temperature': float(row['temperature']) if pd.notna(row['temperature']) else None,
                    'flow_rate': float(row['flow_rate']) if pd.notna(row['flow_rate']) else None,
                    'pressure': float(row['pressure']) if pd.notna(row['pressure']) else None,
                    'total_flow': float(row['total_flow']) if pd.notna(row['total_flow']) else None,
                    'quality_score': float(row['quality_score']) if pd.notna(row['quality_score']) else 0.7,
                    'is_interpolated': False,
                    'raw_data': {
                        'source': source,
                        'district_id': row.get('district_id', 'unknown'),
                        'district_name': row.get('district_name', 'Unknown'),
                        'backfill': True
                    }
                }
                readings.append(reading)
                
            # Insert batch into PostgreSQL
            try:
                inserted = await self.postgres_manager.insert_sensor_readings_batch(readings)
                self.stats['processed_records'] += inserted
                self.stats['total_records'] += len(readings)
                
            except Exception as e:
                logger.error(f"Failed to insert batch from {source}: {e}")
                self.stats['failed_records'] += len(readings)
                
    async def _ensure_nodes_exist(self, node_ids: List[str], df: pd.DataFrame) -> None:
        """Ensure all nodes exist in the nodes table."""
        for node_id in node_ids:
            node_data = df[df['node_id'] == node_id].iloc[0]
            
            node_info = {
                'node_id': str(node_id),
                'node_name': node_data.get('node_name', f'Node {node_id}'),
                'node_type': 'meter',
                'location_name': node_data.get('district_name', 'Unknown'),
                'latitude': None,
                'longitude': None,
                'installation_date': None,
                'last_maintenance_date': None,
                'is_active': True,
                'metadata': {
                    'district_id': node_data.get('district_id', 'unknown'),
                    'district_name': node_data.get('district_name', 'Unknown'),
                    'data_source': 'backfill',
                    'backfill_timestamp': datetime.now().isoformat()
                }
            }
            
            try:
                await self.postgres_manager.upsert_node(node_info)
                self.stats['nodes_processed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to upsert node {node_id}: {e}")
                
    async def _check_existing_data(self, start_date: datetime, end_date: datetime) -> int:
        """Check if data already exists in PostgreSQL."""
        async with self.postgres_manager.acquire() as conn:
            count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM water_infrastructure.sensor_readings
                WHERE timestamp BETWEEN $1 AND $2
            """, start_date, end_date)
            return count
            
    async def _refresh_materialized_views(self) -> None:
        """Refresh materialized views after backfill."""
        logger.info("Refreshing materialized views")
        
        views = [
            'sensor_readings_5min',
            'sensor_readings_hourly',
            'sensor_readings_daily'
        ]
        
        async with self.postgres_manager.acquire() as conn:
            for view in views:
                try:
                    await conn.execute(f"CALL refresh_continuous_aggregate('{view}', NULL, NULL)")
                    logger.info(f"Refreshed materialized view: {view}")
                    
                except Exception as e:
                    logger.error(f"Error refreshing materialized view {view}: {e}")


async def main():
    """Main backfill execution function."""
    parser = argparse.ArgumentParser(description='Network Efficiency ETL Backfill')
    parser.add_argument('--days', type=int, default=90, help='Number of days to backfill')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--force-refresh', action='store_true', help='Force refresh existing data')
    
    args = parser.parse_args()
    
    # Calculate date range
    if args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
    
    backfill = NetworkEfficiencyBackfill()
    
    try:
        await backfill.initialize()
        
        logger.info(f"Starting backfill for {args.days} days ({start_date.date()} to {end_date.date()})")
        
        stats = await backfill.backfill_data(
            start_date=start_date,
            end_date=end_date,
            force_refresh=args.force_refresh
        )
        
        logger.info(f"Backfill completed successfully: {stats}")
        
    except Exception as e:
        logger.error(f"Backfill failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 
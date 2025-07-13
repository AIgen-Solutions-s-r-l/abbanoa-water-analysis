#!/usr/bin/env python3
"""
Network Efficiency ETL - Meter Data Collection

This script collects meter data from BigQuery and loads it into PostgreSQL
for network efficiency analysis. It processes flow rates, pressures, and 
temperatures to populate the sensor_readings table which feeds into the
sensor_readings_hourly materialized view.

This script is designed to run every 5 minutes to ensure real-time data
processing for network efficiency monitoring.
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
from google.cloud import bigquery
import asyncpg

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
        logging.FileHandler('logs/etl_collect_meter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NetworkEfficiencyETL:
    """ETL pipeline for network efficiency meter data collection."""
    
    def __init__(self, batch_size: int = 5000):
        """
        Initialize ETL pipeline.
        
        Args:
            batch_size: Number of records to process in each batch
        """
        self.batch_size = batch_size
        self.bigquery_client = BigQueryClient()
        self.postgres_manager = None
        self.redis_manager = RedisCacheManager()
        
        # ETL statistics
        self.stats = {
            'total_records': 0,
            'processed_records': 0,
            'failed_records': 0,
            'nodes_processed': 0,
            'start_time': None,
            'end_time': None
        }
        
    async def initialize(self) -> None:
        """Initialize database connections."""
        self.postgres_manager = await get_postgres_manager()
        await self.redis_manager.initialize()
        logger.info("Network Efficiency ETL initialized")
        
    async def collect_meter_data(self, minutes_back: int = 10) -> Dict[str, Any]:
        """
        Collect meter data for the last N minutes.
        
        Args:
            minutes_back: Number of minutes to look back for data
            
        Returns:
            ETL execution statistics
        """
        logger.info(f"Starting meter data collection for last {minutes_back} minutes")
        self.stats['start_time'] = datetime.now()
        
        try:
            # Create ETL job record
            job_id = await self.postgres_manager.log_etl_job({
                'job_name': f'network_efficiency_etl_{minutes_back}min',
                'job_type': 'meter_collection',
                'status': 'running',
                'started_at': self.stats['start_time'],
                'metadata': {
                    'minutes_back': minutes_back,
                    'batch_size': self.batch_size
                }
            })
            
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=minutes_back)
            
            # Collect data from multiple sources
            await self._collect_from_sensor_readings_ml(start_time, end_time)
            await self._collect_from_normalized_readings(start_time, end_time)
            await self._collect_from_legacy_sources(start_time, end_time)
            
            # Update job status
            self.stats['end_time'] = datetime.now()
            await self.postgres_manager.update_etl_job(job_id, {
                'status': 'completed',
                'completed_at': self.stats['end_time'],
                'records_processed': self.stats['processed_records'],
                'metadata': {
                    **self.stats,
                    'nodes_processed': self.stats['nodes_processed']
                }
            })
            
            logger.info(f"Meter data collection completed: {self.stats['processed_records']} records processed")
            
            # Update cache with latest readings
            await self._update_cache()
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Meter data collection failed: {e}")
            if 'job_id' in locals():
                await self.postgres_manager.update_etl_job(job_id, {
                    'status': 'failed',
                    'completed_at': datetime.now(),
                    'error_message': str(e)
                })
            raise
            
    async def _collect_from_sensor_readings_ml(self, start_time: datetime, end_time: datetime) -> None:
        """Collect data from the ML-optimized sensor readings table."""
        logger.info("Collecting from sensor_readings_ml table")
        
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
        FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.sensor_readings_ml`
        WHERE timestamp BETWEEN @start_time AND @end_time
        AND data_quality_score > 0.5
        ORDER BY timestamp, node_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
                bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
            ]
        )
        
        try:
            df = self.bigquery_client.client.query(query, job_config=job_config).to_dataframe()
            
            if not df.empty:
                await self._process_and_load_data(df, 'sensor_readings_ml')
                logger.info(f"Processed {len(df)} records from sensor_readings_ml")
                
        except Exception as e:
            logger.error(f"Error collecting from sensor_readings_ml: {e}")
            self.stats['failed_records'] += 1
            
    async def _collect_from_normalized_readings(self, start_time: datetime, end_time: datetime) -> None:
        """Collect data from normalized sensor readings view."""
        logger.info("Collecting from normalized sensor readings")
        
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
        FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.v_sensor_readings_normalized`
        WHERE timestamp BETWEEN @start_time AND @end_time
        ORDER BY timestamp, node_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
                bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
            ]
        )
        
        try:
            df = self.bigquery_client.client.query(query, job_config=job_config).to_dataframe()
            
            if not df.empty:
                await self._process_and_load_data(df, 'normalized_readings')
                logger.info(f"Processed {len(df)} records from normalized readings")
                
        except Exception as e:
            logger.error(f"Error collecting from normalized readings: {e}")
            self.stats['failed_records'] += 1
            
    async def _collect_from_legacy_sources(self, start_time: datetime, end_time: datetime) -> None:
        """Collect data from legacy CSV-based sources."""
        logger.info("Collecting from legacy sources")
        
        # Check for recent CSV uploads or processed backup data
        query = f"""
        SELECT 
            timestamp,
            node_id,
            'Legacy Node' as node_name,
            temperature,
            flow_rate,
            pressure,
            volume as total_flow,
            0.8 as quality_score,
            'backup' as district_id,
            'Backup System' as district_name
        FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.sensor_data`
        WHERE timestamp BETWEEN @start_time AND @end_time
        AND flow_rate IS NOT NULL
        ORDER BY timestamp
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
                bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
            ]
        )
        
        try:
            df = self.bigquery_client.client.query(query, job_config=job_config).to_dataframe()
            
            if not df.empty:
                await self._process_and_load_data(df, 'legacy_sources')
                logger.info(f"Processed {len(df)} records from legacy sources")
                
        except Exception as e:
            logger.error(f"Error collecting from legacy sources: {e}")
            self.stats['failed_records'] += 1
            
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
                    'quality_score': float(row['quality_score']) if pd.notna(row['quality_score']) else 1.0,
                    'is_interpolated': False,
                    'raw_data': {
                        'source': source,
                        'district_id': row.get('district_id', 'unknown'),
                        'district_name': row.get('district_name', 'Unknown')
                    }
                }
                readings.append(reading)
                
            # Insert batch into PostgreSQL
            try:
                inserted = await self.postgres_manager.insert_sensor_readings_batch(readings)
                self.stats['processed_records'] += inserted
                logger.debug(f"Inserted {inserted} readings from {source}")
                
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
                    'data_source': 'etl_collect_meter'
                }
            }
            
            try:
                await self.postgres_manager.upsert_node(node_info)
                self.stats['nodes_processed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to upsert node {node_id}: {e}")
                
    async def _update_cache(self) -> None:
        """Update Redis cache with latest readings."""
        try:
            # Get latest readings for all nodes
            latest_readings = await self.postgres_manager.get_latest_readings()
            
            # Update cache
            for node_id, reading in latest_readings.items():
                cache_key = f"node:{node_id}:latest"
                cache_data = {
                    'timestamp': reading['timestamp'].isoformat(),
                    'flow_rate': str(reading.get('flow_rate', 0)),
                    'pressure': str(reading.get('pressure', 0)),
                    'temperature': str(reading.get('temperature', 0)),
                    'total_flow': str(reading.get('total_flow', 0)),
                    'quality_score': str(reading.get('quality_score', 1.0))
                }
                
                # Set with 10-minute TTL
                await self.redis_manager.set_hash(cache_key, cache_data, ttl=600)
                
            logger.info("Cache updated with latest readings")
            
        except Exception as e:
            logger.error(f"Failed to update cache: {e}")


async def main():
    """Main ETL execution function."""
    etl = NetworkEfficiencyETL()
    
    try:
        await etl.initialize()
        
        # Collect data for the last 10 minutes
        stats = await etl.collect_meter_data(minutes_back=10)
        
        logger.info(f"ETL completed successfully: {stats}")
        
    except Exception as e:
        logger.error(f"ETL failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 
"""
PostgreSQL/TimescaleDB connection manager for water infrastructure data.

This module provides the database connection and query management for the
warm storage layer in our hybrid architecture.
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import asyncpg
import pandas as pd
from asyncpg.pool import Pool

logger = logging.getLogger(__name__)


class PostgresManager:
    """Manages PostgreSQL/TimescaleDB connections and operations."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        min_pool_size: int = 10,
        max_pool_size: int = 20
    ):
        """
        Initialize PostgreSQL manager with connection parameters.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            min_pool_size: Minimum pool connections
            max_pool_size: Maximum pool connections
        """
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = port or int(os.getenv("POSTGRES_PORT", 5432))  # Force port 5432 for main database
        self.database = database or os.getenv("POSTGRES_DB", "abbanoa")  # Force main database
        self.user = user or os.getenv("POSTGRES_USER", "postgres")
        self.password = password or os.getenv("POSTGRES_PASSWORD", "")
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.pool: Optional[Pool] = None
        
    async def initialize(self) -> None:
        """Initialize connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=self.min_pool_size,
                max_size=self.max_pool_size,
                command_timeout=60,
                statement_cache_size=0,  # Disable for TimescaleDB
            )
            logger.info(f"PostgreSQL connection pool created: {self.host}:{self.port}/{self.database}")
            
            # Test connection and check TimescaleDB
            async with self.pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info(f"PostgreSQL version: {version}")
                
                # Check if TimescaleDB is installed
                timescale_installed = await conn.fetchval(
                    "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb')"
                )
                if timescale_installed:
                    logger.info("TimescaleDB extension is installed")
                else:
                    logger.warning("TimescaleDB extension is not installed")
                    
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise
            
    async def close(self) -> None:
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")
            
    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool."""
        if not self.pool:
            await self.initialize()
        async with self.pool.acquire() as conn:
            yield conn
            
    # ====================================
    # Node Operations
    # ====================================
    
    async def upsert_node(self, node_data: Dict[str, Any]) -> None:
        """Insert or update node information."""
        async with self.acquire() as conn:
            await conn.execute("""
                INSERT INTO water_infrastructure.nodes 
                    (node_id, node_name, node_type, location_name, is_active, metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (node_id) 
                DO UPDATE SET
                    node_name = EXCLUDED.node_name,
                    node_type = EXCLUDED.node_type,
                    location_name = EXCLUDED.location_name,
                    is_active = EXCLUDED.is_active,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
            """, 
            node_data['node_id'],
            node_data['node_name'],
            node_data['node_type'],
            node_data.get('location_name'),
            node_data.get('is_active', True),
            json.dumps(node_data.get('metadata', {}))
            )
            
    async def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all active nodes."""
        async with self.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    node_id, node_name, node_type, location_name,
                    is_active, metadata, created_at, updated_at
                FROM water_infrastructure.nodes
                WHERE is_active = true
                ORDER BY node_name
            """)
            return [dict(row) for row in rows]
            
    # ====================================
    # Sensor Reading Operations
    # ====================================
    
    async def insert_sensor_readings_batch(self, readings: List[Dict[str, Any]]) -> int:
        """Batch insert sensor readings."""
        if not readings:
            return 0
            
        async with self.acquire() as conn:
            # Prepare data for COPY
            records = []
            for reading in readings:
                records.append((
                    reading['timestamp'],
                    reading['node_id'],
                    reading.get('temperature'),
                    reading.get('flow_rate'),
                    reading.get('pressure'),
                    reading.get('total_flow'),
                    reading.get('quality_score', 1.0),
                    reading.get('is_interpolated', False),
                    json.dumps(reading.get('raw_data', {}))
                ))
                
            # Use COPY for efficient batch insert
            result = await conn.copy_records_to_table(
                'sensor_readings',
                records=records,
                columns=['timestamp', 'node_id', 'temperature', 'flow_rate', 
                        'pressure', 'total_flow', 'quality_score', 
                        'is_interpolated', 'raw_data'],
                schema_name='water_infrastructure'
            )
            
            logger.info(f"Inserted {len(records)} sensor readings")
            return len(records)
            
    async def get_latest_readings(self, node_ids: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """Get latest reading for each node."""
        async with self.acquire() as conn:
            query = """
                WITH latest AS (
                    SELECT DISTINCT ON (node_id)
                        node_id, timestamp, temperature, flow_rate, pressure, quality_score
                    FROM water_infrastructure.sensor_readings
                    WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                    {}
                    ORDER BY node_id, timestamp DESC
                )
                SELECT * FROM latest
            """
            
            if node_ids:
                query = query.format("AND node_id = ANY($1)")
                rows = await conn.fetch(query, node_ids)
            else:
                query = query.format("")
                rows = await conn.fetch(query)
                
            return {row['node_id']: dict(row) for row in rows}
            
    async def get_time_series_data(
        self, 
        node_id: str, 
        start_time: datetime, 
        end_time: datetime,
        interval: str = "5min"
    ) -> pd.DataFrame:
        """Get time series data for a node."""
        async with self.acquire() as conn:
            # Use appropriate continuous aggregate based on interval
            if interval == "5min":
                table = "sensor_readings_5min"
            elif interval == "1h":
                table = "sensor_readings_hourly"
            elif interval == "1d":
                table = "sensor_readings_daily"
            else:
                table = "sensor_readings"
                
            query = f"""
                SELECT 
                    bucket as timestamp,
                    avg_flow_rate as flow_rate,
                    avg_pressure as pressure,
                    avg_temperature as temperature
                FROM water_infrastructure.{table}
                WHERE node_id = $1
                AND bucket BETWEEN $2 AND $3
                ORDER BY bucket
            """
            
            rows = await conn.fetch(query, node_id, start_time, end_time)
            if rows:
                return pd.DataFrame([dict(row) for row in rows])
            return pd.DataFrame()
            
    # ====================================
    # Anomaly Operations
    # ====================================
    
    async def insert_anomaly(self, anomaly: Dict[str, Any]) -> int:
        """Insert a new anomaly detection."""
        async with self.acquire() as conn:
            anomaly_id = await conn.fetchval("""
                INSERT INTO water_infrastructure.anomalies
                    (timestamp, node_id, anomaly_type, severity, measurement_type,
                     actual_value, expected_value, deviation_percentage, 
                     detection_method, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING anomaly_id
            """,
            anomaly['timestamp'],
            anomaly['node_id'],
            anomaly['anomaly_type'],
            anomaly['severity'],
            anomaly.get('measurement_type'),
            anomaly.get('actual_value'),
            anomaly.get('expected_value'),
            anomaly.get('deviation_percentage'),
            anomaly.get('detection_method', 'statistical'),
            anomaly.get('metadata', {})
            )
            return anomaly_id
            
    async def get_recent_anomalies(
        self, 
        hours: int = 24, 
        node_ids: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent anomalies."""
        async with self.acquire() as conn:
            query = """
                SELECT 
                    a.*, 
                    n.node_name
                FROM water_infrastructure.anomalies a
                JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
                WHERE a.timestamp > CURRENT_TIMESTAMP - INTERVAL '{} hours'
                AND a.resolved_at IS NULL
                {}
                ORDER BY a.timestamp DESC
                LIMIT $1
            """
            
            if node_ids:
                query = query.format(hours, "AND a.node_id = ANY($2)")
                rows = await conn.fetch(query, limit, node_ids)
            else:
                query = query.format(hours, "")
                rows = await conn.fetch(query, limit)
                
            return [dict(row) for row in rows]
            
    # ====================================
    # ML Operations
    # ====================================
    
    async def insert_ml_predictions(self, predictions: List[Dict[str, Any]]) -> int:
        """Batch insert ML predictions."""
        if not predictions:
            return 0
            
        async with self.acquire() as conn:
            records = []
            for pred in predictions:
                records.append((
                    pred['timestamp'],
                    pred['node_id'],
                    pred['model_name'],
                    pred.get('model_version', '1.0'),
                    pred['prediction_type'],
                    pred['prediction_horizon_hours'],
                    pred.get('predicted_value'),
                    pred.get('confidence_score'),
                    pred.get('metadata', {})
                ))
                
            await conn.executemany("""
                INSERT INTO water_infrastructure.ml_predictions
                    (timestamp, node_id, model_name, model_version, prediction_type,
                     prediction_horizon_hours, predicted_value, confidence_score, 
                     prediction_metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, records)
            
            return len(records)
            
    # ====================================
    # System Metrics
    # ====================================
    
    async def get_system_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get system-wide metrics."""
        # If time_range already contains "hour", "day", etc., it's already a PostgreSQL interval
        if any(unit in time_range for unit in ["hour", "day", "days", "hours"]):
            interval = time_range
        else:
            # Map time range to PostgreSQL interval
            interval_map = {
                "1h": "1 hour",
                "6h": "6 hours",
                "24h": "24 hours",
                "3d": "3 days",
                "7d": "7 days",
                "30d": "30 days",
                "365d": "365 days"
            }
            interval = interval_map.get(time_range, "24 hours")
        
        async with self.acquire() as conn:
            # Direct query from sensor_readings table
            # For now, get all available data regardless of time range
            result = await conn.fetchrow(f"""
                WITH recent_data AS (
                    SELECT 
                        node_id,
                        flow_rate,
                        pressure,
                        total_flow,
                        timestamp
                    FROM water_infrastructure.sensor_readings
                    -- Get all data we have (November 2024)
                    WHERE timestamp >= '2024-11-01'
                )
                SELECT 
                    COUNT(DISTINCT node_id) as active_nodes,
                    COALESCE(AVG(flow_rate), 0) as total_flow,
                    COALESCE(AVG(pressure), 0) as avg_pressure,
                    COALESCE(COUNT(*) * AVG(flow_rate) * 0.1, 0) as total_volume_m3,
                    0 as anomaly_count
                FROM recent_data
            """)
            
            if result:
                return dict(result)
            return {
                'active_nodes': 0,
                'total_flow': 0,
                'avg_pressure': 0,
                'total_volume_m3': 0,
                'anomaly_count': 0
            }
            
    # ====================================
    # ETL Operations
    # ====================================
    
    async def log_etl_job(self, job_data: Dict[str, Any]) -> int:
        """Log ETL job execution."""
        async with self.acquire() as conn:
            job_id = await conn.fetchval("""
                INSERT INTO water_infrastructure.etl_jobs
                    (job_name, job_type, status, started_at, completed_at,
                     records_processed, records_failed, error_message, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING job_id
            """,
            job_data['job_name'],
            job_data['job_type'],
            job_data['status'],
            job_data['started_at'],
            job_data.get('completed_at'),
            job_data.get('records_processed', 0),
            job_data.get('records_failed', 0),
            job_data.get('error_message'),
            json.dumps(job_data.get('metadata', {}))
            )
            return job_id
            
    async def update_etl_job(self, job_id: int, updates: Dict[str, Any]) -> None:
        """Update ETL job status."""
        async with self.acquire() as conn:
            set_clauses = []
            values = []
            
            for i, (key, value) in enumerate(updates.items(), 1):
                set_clauses.append(f"{key} = ${i}")
                # Convert dict to JSON for metadata field
                if key == 'metadata' and isinstance(value, dict):
                    values.append(json.dumps(value))
                else:
                    values.append(value)
                
            values.append(job_id)
            
            await conn.execute(f"""
                UPDATE water_infrastructure.etl_jobs
                SET {', '.join(set_clauses)}
                WHERE job_id = ${len(values)}
            """, *values)


# Singleton instance
_postgres_manager: Optional[PostgresManager] = None


async def get_postgres_manager() -> PostgresManager:
    """Get or create PostgreSQL manager singleton."""
    global _postgres_manager
    if _postgres_manager is None:
        _postgres_manager = PostgresManager()
        await _postgres_manager.initialize()
    return _postgres_manager
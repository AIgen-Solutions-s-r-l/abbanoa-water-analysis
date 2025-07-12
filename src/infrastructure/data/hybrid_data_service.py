"""
Hybrid data service that coordinates between BigQuery, PostgreSQL, and Redis.

This service implements the three-tier architecture:
- BigQuery: Cold storage (historical data)
- PostgreSQL: Warm storage (operational data)
- Redis: Hot cache (real-time data)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import json
from enum import Enum

from google.cloud import bigquery
from src.infrastructure.database.postgres_manager import get_postgres_manager, PostgresManager
from src.infrastructure.cache.redis_cache_manager import RedisCacheManager
from src.infrastructure.bigquery.bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)


class DataTier(Enum):
    """Data storage tiers."""
    HOT = "redis"      # Last 24 hours
    WARM = "postgres"  # Last 90 days
    COLD = "bigquery"  # Historical


class HybridDataService:
    """
    Manages data across three tiers with intelligent routing and caching.
    
    Data Flow:
    1. New data → Redis (immediate) → PostgreSQL (batch) → BigQuery (daily)
    2. Queries → Redis → PostgreSQL → BigQuery (fallback chain)
    """
    
    def __init__(
        self,
        redis_manager: Optional[RedisCacheManager] = None,
        cache_ttl_hours: int = 24
    ):
        """Initialize hybrid data service."""
        self.redis_manager = redis_manager or RedisCacheManager()
        self.postgres_manager = None
        self.bigquery_client = BigQueryClient()
        self.cache_ttl_hours = cache_ttl_hours
        
        # Write buffer for batch operations
        self.write_buffer = []
        self.buffer_size = 1000
        self.last_flush = datetime.now()
        
    async def initialize(self) -> None:
        """Initialize all data tier connections."""
        logger.info("Initializing hybrid data service...")
        
        # Initialize PostgreSQL with correct connection parameters
        # Use the processing database with actual data
        self.postgres_manager = PostgresManager(
            host="localhost",
            port=5434,  # Processing database port
            database="abbanoa_processing",  # Processing database with actual data
            user="abbanoa_user",
            password="abbanoa_secure_pass",
            min_pool_size=2,  # Reduce pool size to avoid conflicts
            max_pool_size=5
        )
        await self.postgres_manager.initialize()
        
        # Initialize Redis cache
        self.redis_manager.initialize_cache()
        
        # Start background tasks (only if not in Streamlit context)
        try:
            # Check if we're in a Streamlit context to avoid background task conflicts
            import streamlit as st
            # Check if we have an active Streamlit session
            if hasattr(st, 'session_state'):
                logger.info("Skipping background sync in Streamlit context")
            else:
                logger.info("Starting background sync task")
                asyncio.create_task(self._background_sync())
        except (ImportError, AttributeError):
            # Not in Streamlit, safe to start background task
            logger.info("Starting background sync task")
            asyncio.create_task(self._background_sync())
        
        logger.info("Hybrid data service initialized")
        
    # ====================================
    # Write Operations (Write-Through Cache)
    # ====================================
    
    async def write_sensor_reading(self, reading: Dict[str, Any]) -> None:
        """
        Write sensor reading using write-through cache pattern.
        
        Flow: Redis → Buffer → PostgreSQL → BigQuery (daily)
        """
        node_id = reading['node_id']
        timestamp = reading['timestamp']
        
        # 1. Write to Redis immediately
        await self._write_to_redis(reading)
        
        # 2. Add to write buffer
        self.write_buffer.append(reading)
        
        # 3. Flush buffer if needed
        if len(self.write_buffer) >= self.buffer_size or \
           (datetime.now() - self.last_flush) > timedelta(minutes=5):
            await self._flush_write_buffer()
            
        # 4. Update real-time metrics
        await self._update_realtime_metrics(reading)
        
        # 5. Check for anomalies
        await self._check_anomalies(reading)
        
    async def _write_to_redis(self, reading: Dict[str, Any]) -> None:
        """Write reading to Redis cache."""
        node_id = reading['node_id']
        
        # Store latest reading
        self.redis_manager.redis_client.hset(
            f"node:{node_id}:latest",
            mapping={
                "timestamp": reading['timestamp'].isoformat(),
                "flow_rate": reading.get('flow_rate', 0),
                "pressure": reading.get('pressure', 0),
                "temperature": reading.get('temperature', 0)
            }
        )
        
        # Add to time series (last 24h)
        score = reading['timestamp'].timestamp()
        value = json.dumps({
            "flow_rate": reading.get('flow_rate', 0),
            "pressure": reading.get('pressure', 0),
            "temperature": reading.get('temperature', 0)
        })
        
        self.redis_manager.redis_client.zadd(
            f"node:{node_id}:timeseries",
            {value: score}
        )
        
        # Trim old data (keep 24h)
        cutoff = (datetime.now() - timedelta(hours=24)).timestamp()
        self.redis_manager.redis_client.zremrangebyscore(
            f"node:{node_id}:timeseries",
            0, cutoff
        )
        
    async def _flush_write_buffer(self) -> None:
        """Flush write buffer to PostgreSQL."""
        if not self.write_buffer:
            return
            
        try:
            # Batch insert to PostgreSQL
            await self.postgres_manager.insert_sensor_readings_batch(
                self.write_buffer
            )
            
            # Log ETL job
            await self.postgres_manager.log_etl_job({
                "job_name": "sensor_reading_batch_insert",
                "job_type": "write_through",
                "status": "completed",
                "started_at": self.last_flush,
                "completed_at": datetime.now(),
                "records_processed": len(self.write_buffer)
            })
            
            logger.info(f"Flushed {len(self.write_buffer)} readings to PostgreSQL")
            
            # Clear buffer
            self.write_buffer = []
            self.last_flush = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to flush write buffer: {e}")
            # Keep buffer for retry
            
    # ====================================
    # Read Operations (Tiered Queries)
    # ====================================
    
    async def get_node_data(
        self,
        node_id: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = "5min"
    ) -> pd.DataFrame:
        """
        Get node data using tiered storage strategy.
        
        Query order: Redis → PostgreSQL → BigQuery
        """
        cache_key = f"node:{node_id}:data:{start_time.date()}:{end_time.date()}:{interval}"
        
        # Check which tier to query based on time range
        tier = self._determine_tier(start_time)
        
        if tier == DataTier.HOT:
            # Try Redis first
            data = await self._query_redis_timeseries(node_id, start_time, end_time)
            if data is not None:
                return data
                
        if tier in [DataTier.HOT, DataTier.WARM]:
            # Try PostgreSQL
            data = await self._query_postgres(node_id, start_time, end_time, interval)
            if data is not None and not data.empty:
                # Cache in Redis for next time
                self._cache_dataframe(cache_key, data)
                return data
                
        # Fallback to BigQuery
        data = await self._query_bigquery(node_id, start_time, end_time)
        
        # Cache in Redis and potentially warm up PostgreSQL
        if data is not None and not data.empty:
            self._cache_dataframe(cache_key, data)
            # TODO: Consider warming PostgreSQL cache
            return data
            
        # Return empty DataFrame if no data found in any tier
        return pd.DataFrame()
        
    async def get_latest_readings(
        self,
        node_ids: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get latest readings for nodes."""
        # Always check Redis first for latest data
        latest_readings = {}
        
        if node_ids is None:
            # Get all nodes
            node_ids = self.redis_manager.redis_client.lrange("nodes:all", 0, -1)
            
        for node_id in node_ids:
            # Try Redis
            latest = self.redis_manager.redis_client.hgetall(f"node:{node_id}:latest")
            if latest:
                latest_readings[node_id] = {
                    k.decode() if isinstance(k, bytes) else k: 
                    v.decode() if isinstance(v, bytes) else v 
                    for k, v in latest.items()
                }
            else:
                # Fallback to PostgreSQL
                pg_latest = await self.postgres_manager.get_latest_readings([node_id])
                if node_id in pg_latest:
                    latest_readings[node_id] = pg_latest[node_id]
                    # Cache in Redis
                    self.redis_manager.redis_client.hset(
                        f"node:{node_id}:latest",
                        mapping=pg_latest[node_id]
                    )
                    
        return latest_readings
        
    async def get_system_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get system-wide metrics."""
        cache_key = f"system:metrics:{time_range}"
        
        # Check Redis cache
        cached = self.redis_manager.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
            
        # Query PostgreSQL
        metrics = await self.postgres_manager.get_system_metrics(time_range)
        
        # Cache for 5 minutes
        self.redis_manager.redis_client.setex(
            cache_key,
            300,  # 5 minutes
            json.dumps(metrics, default=str)
        )
        
        return metrics
        
    # ====================================
    # Anomaly Detection
    # ====================================
    
    async def _check_anomalies(self, reading: Dict[str, Any]) -> None:
        """Check for anomalies in real-time."""
        node_id = reading['node_id']
        
        # Get recent average from Redis
        recent_data = await self._get_recent_stats(node_id)
        
        if recent_data:
            # Simple threshold-based detection
            flow_rate = reading.get('flow_rate', 0)
            avg_flow = recent_data.get('avg_flow', 0)
            std_flow = recent_data.get('std_flow', 1)
            
            # Check for anomalies (3-sigma rule)
            if abs(flow_rate - avg_flow) > 3 * std_flow:
                anomaly = {
                    'timestamp': reading['timestamp'],
                    'node_id': node_id,
                    'anomaly_type': 'flow_spike' if flow_rate > avg_flow else 'flow_drop',
                    'severity': 'warning',
                    'measurement_type': 'flow_rate',
                    'actual_value': flow_rate,
                    'expected_value': avg_flow,
                    'deviation_percentage': abs((flow_rate - avg_flow) / avg_flow * 100)
                }
                
                # Store in Redis
                self.redis_manager.redis_client.zadd(
                    "anomalies:recent",
                    {json.dumps(anomaly, default=str): reading['timestamp'].timestamp()}
                )
                
                # Queue for PostgreSQL insert
                # TODO: Implement anomaly queue
                
    async def _get_recent_stats(self, node_id: str) -> Optional[Dict[str, float]]:
        """Get recent statistics for anomaly detection."""
        # Get last hour of data from Redis
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        data = await self._query_redis_timeseries(node_id, start_time, end_time)
        
        if data is not None and len(data) > 10:
            return {
                'avg_flow': data['flow_rate'].mean(),
                'std_flow': data['flow_rate'].std(),
                'avg_pressure': data['pressure'].mean(),
                'std_pressure': data['pressure'].std()
            }
        return None
        
    # ====================================
    # Helper Methods
    # ====================================
    
    def _determine_tier(self, timestamp: datetime) -> DataTier:
        """Determine which storage tier to query based on timestamp."""
        age = datetime.now() - timestamp
        
        if age <= timedelta(hours=24):
            return DataTier.HOT
        elif age <= timedelta(days=90):
            return DataTier.WARM
        else:
            return DataTier.COLD
            
    async def _query_redis_timeseries(
        self,
        node_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[pd.DataFrame]:
        """Query time series data from Redis."""
        try:
            # Get data from sorted set
            data = self.redis_manager.redis_client.zrangebyscore(
                f"node:{node_id}:timeseries",
                start_time.timestamp(),
                end_time.timestamp()
            )
            
            if data:
                records = []
                for item in data:
                    record = json.loads(item)
                    records.append(record)
                    
                df = pd.DataFrame(records)
                return df
            return None
            
        except Exception as e:
            logger.error(f"Redis query failed: {e}")
            return None
            
    async def _query_postgres(
        self,
        node_id: str,
        start_time: datetime,
        end_time: datetime,
        interval: str
    ) -> Optional[pd.DataFrame]:
        """Query data from PostgreSQL."""
        try:
            # Check if postgres manager is available and healthy
            if not self.postgres_manager or not self.postgres_manager.pool:
                logger.warning("PostgreSQL manager not available")
                return pd.DataFrame()
                
            result = await self.postgres_manager.get_time_series_data(
                node_id, start_time, end_time, interval
            )
            return result if result is not None else pd.DataFrame()
        except Exception as e:
            logger.error(f"PostgreSQL query failed: {e}")
            return pd.DataFrame()
            
    async def _query_bigquery(
        self,
        node_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[pd.DataFrame]:
        """Query data from BigQuery."""
        try:
            # Skip BigQuery if client is not properly initialized
            if not hasattr(self.bigquery_client, 'client') or self.bigquery_client.client is None:
                logger.warning("BigQuery client not properly initialized, skipping BigQuery query")
                return pd.DataFrame()
                
            query = f"""
            SELECT 
                timestamp,
                temperature,
                flow_rate,
                pressure
            FROM `{self.bigquery_client.dataset_id}.sensor_readings`
            WHERE node_id = @node_id
            AND timestamp BETWEEN @start_time AND @end_time
            ORDER BY timestamp
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("node_id", "STRING", node_id),
                    bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
                    bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
                ]
            )
            
            df = self.bigquery_client.client.query(query, job_config=job_config).to_dataframe()
            return df
            
        except Exception as e:
            logger.error(f"BigQuery query failed: {e}")
            return pd.DataFrame()
            
    def _cache_dataframe(self, key: str, df: pd.DataFrame) -> None:
        """Cache DataFrame in Redis."""
        try:
            # Convert to JSON for caching
            data = df.to_json(orient='records', date_format='iso')
            self.redis_manager.redis_client.setex(
                key,
                3600,  # 1 hour TTL
                data
            )
        except Exception as e:
            logger.error(f"Failed to cache dataframe: {e}")
            
    async def _update_realtime_metrics(self, reading: Dict[str, Any]) -> None:
        """Update real-time metrics in Redis."""
        # Update system flow total
        flow_rate = reading.get('flow_rate', 0)
        self.redis_manager.redis_client.incrbyfloat('system:total_flow', flow_rate)
        
        # Update node count
        self.redis_manager.redis_client.sadd('system:active_nodes', reading['node_id'])
        
    # ====================================
    # Background Tasks
    # ====================================
    
    async def _background_sync(self) -> None:
        """Background task to sync data between tiers."""
        while True:
            try:
                # Flush write buffer every 5 minutes
                await asyncio.sleep(300)
                
                # Check if postgres manager is still valid
                if self.postgres_manager and self.postgres_manager.pool:
                    await self._flush_write_buffer()
                else:
                    logger.warning("PostgreSQL manager not available, skipping flush")
                
                # TODO: Implement PostgreSQL → BigQuery sync
                # TODO: Implement cache warming
                # TODO: Clean up old Redis data
                
            except asyncio.CancelledError:
                logger.info("Background sync task cancelled")
                break
            except Exception as e:
                logger.error(f"Background sync error: {e}")
                # Wait a bit before retrying to avoid tight error loops
                await asyncio.sleep(60)
                
                
# Singleton instance
_hybrid_service: Optional[HybridDataService] = None


async def get_hybrid_data_service() -> HybridDataService:
    """Get or create hybrid data service singleton."""
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridDataService()
        await _hybrid_service.initialize()
    return _hybrid_service
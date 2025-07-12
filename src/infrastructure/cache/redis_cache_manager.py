"""
Redis cache manager for pre-processed water infrastructure data.

This module handles caching of pre-computed metrics, anomalies, and time-series data
to avoid repeated BigQuery queries and improve dashboard performance.
"""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

import pandas as pd
import redis

logger = logging.getLogger(__name__)


class RedisCacheManager:
    """Manages Redis cache for water infrastructure data."""

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        ttl_hours: int = 24,
    ):
        """Initialize Redis connection and settings."""
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db, decode_responses=True
        )
        self.ttl_seconds = ttl_hours * 3600

    def initialize_cache(self, force_refresh: bool = False) -> None:
        """Initialize cache with pre-processed data from BigQuery."""
        logger.info("Initializing Redis cache...")

        # Check if cache is already initialized
        if not force_refresh and self.redis_client.exists("cache:initialized"):
            logger.info("Cache already initialized. Use force_refresh=True to reload.")
            return

        # Load data in parallel
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []

            # Submit tasks for each data type
            futures.append(executor.submit(self._cache_node_metadata))
            futures.append(executor.submit(self._cache_latest_readings))
            futures.append(executor.submit(self._cache_aggregated_metrics))
            futures.append(executor.submit(self._cache_anomalies))
            futures.append(executor.submit(self._cache_time_series_data))

            # Wait for all tasks to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error during cache initialization: {e}")

        # Mark cache as initialized
        self.redis_client.setex("cache:initialized", self.ttl_seconds, "true")
        logger.info("Cache initialization complete!")

    def _cache_node_metadata(self) -> None:
        """Cache node metadata and mappings."""
        logger.info("Caching node metadata...")

        # Get distinct nodes from sensor_readings_ml
        query = """
        SELECT DISTINCT
            node_id,
            node_name,
            node_type,
            district_id
        FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
        """

        df = self.bigquery_client.query(query).to_dataframe()

        # Store each node's metadata
        for _, row in df.iterrows():
            key = f"node:{row['node_id']}:metadata"
            value = {
                "node_id": row["node_id"],
                "node_name": row["node_name"],
                "node_type": row["node_type"],
                "district_id": row["district_id"],
            }
            self.redis_client.hset(key, mapping=value)
            self.redis_client.expire(key, self.ttl_seconds)

        # Store list of all node IDs
        node_ids = df["node_id"].tolist()
        self.redis_client.lpush("nodes:all", *node_ids)
        self.redis_client.expire("nodes:all", self.ttl_seconds)

        logger.info(f"Cached metadata for {len(node_ids)} nodes")

    def _cache_latest_readings(self) -> None:
        """Cache latest sensor readings for each node."""
        logger.info("Caching latest readings...")

        query = """
        WITH latest_readings AS (
            SELECT
                node_id,
                timestamp,
                flow_rate,
                pressure,
                temperature,
                volume,
                ROW_NUMBER() OVER (PARTITION BY node_id ORDER BY timestamp DESC) as rn
            FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        )
        SELECT * EXCEPT(rn)
        FROM latest_readings
        WHERE rn = 1
        """

        df = self.bigquery_client.query(query).to_dataframe()

        # Cache latest reading for each node
        for _, row in df.iterrows():
            key = f"node:{row['node_id']}:latest"
            value = {
                "timestamp": row["timestamp"].isoformat(),
                "flow_rate": (
                    float(row["flow_rate"]) if pd.notna(row["flow_rate"]) else 0
                ),
                "pressure": float(row["pressure"]) if pd.notna(row["pressure"]) else 0,
                "temperature": (
                    float(row["temperature"]) if pd.notna(row["temperature"]) else 0
                ),
                "volume": float(row["volume"]) if pd.notna(row["volume"]) else 0,
            }
            self.redis_client.hset(key, mapping={k: str(v) for k, v in value.items()})
            self.redis_client.expire(key, self.ttl_seconds)

        logger.info(f"Cached latest readings for {len(df)} nodes")

    def _cache_aggregated_metrics(self) -> None:
        """Cache pre-aggregated metrics for different time ranges."""
        logger.info("Caching aggregated metrics...")

        time_ranges = [
            ("1h", 1),
            ("6h", 6),
            ("24h", 24),
            ("3d", 72),
            ("7d", 168),
            ("30d", 720),
        ]

        for range_name, hours in time_ranges:
            query = f"""
            SELECT
                node_id,
                COUNT(*) as reading_count,
                AVG(flow_rate) as avg_flow,
                MIN(flow_rate) as min_flow,
                MAX(flow_rate) as max_flow,
                STDDEV(flow_rate) as stddev_flow,
                AVG(pressure) as avg_pressure,
                MIN(pressure) as min_pressure,
                MAX(pressure) as max_pressure,
                SUM(CASE WHEN flow_rate > 0 THEN 1 ELSE 0 END) / COUNT(*) as uptime_percentage
            FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {hours} HOUR)
            GROUP BY node_id
            """

            df = self.bigquery_client.query(query).to_dataframe()

            # Store aggregated metrics for each node
            for _, row in df.iterrows():
                key = f"node:{row['node_id']}:metrics:{range_name}"
                metrics = {
                    "reading_count": int(row["reading_count"]),
                    "avg_flow": (
                        float(row["avg_flow"]) if pd.notna(row["avg_flow"]) else 0
                    ),
                    "min_flow": (
                        float(row["min_flow"]) if pd.notna(row["min_flow"]) else 0
                    ),
                    "max_flow": (
                        float(row["max_flow"]) if pd.notna(row["max_flow"]) else 0
                    ),
                    "stddev_flow": (
                        float(row["stddev_flow"]) if pd.notna(row["stddev_flow"]) else 0
                    ),
                    "avg_pressure": (
                        float(row["avg_pressure"])
                        if pd.notna(row["avg_pressure"])
                        else 0
                    ),
                    "min_pressure": (
                        float(row["min_pressure"])
                        if pd.notna(row["min_pressure"])
                        else 0
                    ),
                    "max_pressure": (
                        float(row["max_pressure"])
                        if pd.notna(row["max_pressure"])
                        else 0
                    ),
                    "uptime_percentage": (
                        float(row["uptime_percentage"])
                        if pd.notna(row["uptime_percentage"])
                        else 0
                    ),
                }
                self.redis_client.hset(
                    key, mapping={k: str(v) for k, v in metrics.items()}
                )
                self.redis_client.expire(key, self.ttl_seconds)

            # Store system-wide metrics
            system_key = f"system:metrics:{range_name}"
            system_metrics = {
                "total_nodes": len(df),
                "active_nodes": len(df[df["uptime_percentage"] > 0.1]),
                "total_flow": float(df["avg_flow"].sum()),
                "avg_pressure": float(df["avg_pressure"].mean()) if not df.empty else 0,
            }
            self.redis_client.hset(
                system_key, mapping={k: str(v) for k, v in system_metrics.items()}
            )
            self.redis_client.expire(system_key, self.ttl_seconds)

        logger.info("Cached aggregated metrics for all time ranges")

    def _cache_anomalies(self) -> None:
        """Cache detected anomalies."""
        logger.info("Caching anomalies...")

        # Detect anomalies using statistical methods
        query = """
        WITH stats AS (
            SELECT
                node_id,
                timestamp,
                flow_rate,
                pressure,
                AVG(flow_rate) OVER w as avg_flow,
                STDDEV(flow_rate) OVER w as stddev_flow,
                AVG(pressure) OVER w as avg_pressure,
                STDDEV(pressure) OVER w as stddev_pressure
            FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            WINDOW w AS (PARTITION BY node_id ORDER BY timestamp ROWS BETWEEN 48 PRECEDING AND CURRENT ROW)
        )
        SELECT
            node_id,
            timestamp,
            flow_rate,
            pressure,
            avg_flow,
            stddev_flow,
            avg_pressure,
            stddev_pressure,
            CASE
                WHEN flow_rate > avg_flow + 3 * stddev_flow THEN 'high_flow'
                WHEN flow_rate < avg_flow - 3 * stddev_flow THEN 'low_flow'
                WHEN pressure > avg_pressure + 3 * stddev_pressure THEN 'high_pressure'
                WHEN pressure < avg_pressure - 3 * stddev_pressure THEN 'low_pressure'
                ELSE NULL
            END as anomaly_type
        FROM stats
        WHERE (
            flow_rate > avg_flow + 3 * stddev_flow OR
            flow_rate < avg_flow - 3 * stddev_flow OR
            pressure > avg_pressure + 3 * stddev_pressure OR
            pressure < avg_pressure - 3 * stddev_pressure
        )
        ORDER BY timestamp DESC
        LIMIT 1000
        """

        df = self.bigquery_client.query(query).to_dataframe()

        # Store anomalies
        anomalies = []
        for _, row in df.iterrows():
            anomaly = {
                "node_id": row["node_id"],
                "timestamp": row["timestamp"].isoformat(),
                "anomaly_type": row["anomaly_type"],
                "flow_rate": (
                    float(row["flow_rate"]) if pd.notna(row["flow_rate"]) else 0
                ),
                "pressure": float(row["pressure"]) if pd.notna(row["pressure"]) else 0,
            }
            anomalies.append(json.dumps(anomaly))

        if anomalies:
            self.redis_client.lpush("anomalies:recent", *anomalies)
            self.redis_client.ltrim("anomalies:recent", 0, 999)  # Keep only latest 1000
            self.redis_client.expire("anomalies:recent", self.ttl_seconds)

        logger.info(f"Cached {len(anomalies)} anomalies")

    def _cache_time_series_data(self) -> None:
        """Cache time series data for quick chart rendering."""
        logger.info("Caching time series data...")

        # Cache hourly aggregates for the last 7 days
        query = """
        SELECT
            TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
            node_id,
            AVG(flow_rate) as avg_flow,
            AVG(pressure) as avg_pressure
        FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        GROUP BY hour, node_id
        ORDER BY hour DESC
        """

        df = self.bigquery_client.query(query).to_dataframe()

        # Group by node and store time series
        for node_id in df["node_id"].unique():
            node_data = df[df["node_id"] == node_id].sort_values("hour")

            # Store as JSON time series
            time_series = {
                "timestamps": node_data["hour"]
                .dt.strftime("%Y-%m-%d %H:%M:%S")
                .tolist(),
                "flow_rates": node_data["avg_flow"].fillna(0).tolist(),
                "pressures": node_data["avg_pressure"].fillna(0).tolist(),
            }

            key = f"node:{node_id}:timeseries:7d"
            self.redis_client.set(key, json.dumps(time_series))
            self.redis_client.expire(key, self.ttl_seconds)

        logger.info(f"Cached time series data for {df['node_id'].nunique()} nodes")

    # Getter methods for dashboard
    def get_latest_reading(self, node_id: str) -> Dict[str, Any]:
        """Get latest reading for a node from cache."""
        key = f"node:{node_id}:latest"
        data = self.redis_client.hgetall(key)
        if data:
            return {
                "timestamp": data.get("timestamp"),
                "flow_rate": float(data.get("flow_rate", 0)),
                "pressure": float(data.get("pressure", 0)),
                "temperature": float(data.get("temperature", 0)),
                "volume": float(data.get("volume", 0)),
            }
        return {}

    def get_node_metrics(self, node_id: str, time_range: str = "24h") -> Dict[str, Any]:
        """Get aggregated metrics for a node."""
        key = f"node:{node_id}:metrics:{time_range}"
        data = self.redis_client.hgetall(key)
        if data:
            return {k: float(v) if v != "None" else 0 for k, v in data.items()}
        return {}

    def get_system_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get system-wide metrics."""
        key = f"system:metrics:{time_range}"
        data = self.redis_client.hgetall(key)
        if data:
            return {k: float(v) if v != "None" else 0 for k, v in data.items()}
        return {}

    def get_recent_anomalies(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent anomalies from cache."""
        anomalies = self.redis_client.lrange("anomalies:recent", 0, limit - 1)
        return [json.loads(a) for a in anomalies]

    def get_time_series(self, node_id: str) -> Dict[str, List]:
        """Get time series data for a node."""
        key = f"node:{node_id}:timeseries:7d"
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return {"timestamps": [], "flow_rates": [], "pressures": []}

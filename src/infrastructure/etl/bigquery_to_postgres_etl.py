"""
ETL pipeline for syncing data from BigQuery to PostgreSQL.

This module handles the daily data synchronization from BigQuery (cold storage)
to PostgreSQL/TimescaleDB (warm storage) as part of the hybrid architecture.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from google.cloud import bigquery

from src.infrastructure.bigquery.bigquery_client import BigQueryClient
from src.infrastructure.cache.redis_cache_manager import RedisCacheManager
from src.infrastructure.database.postgres_manager import get_postgres_manager

logger = logging.getLogger(__name__)


class BigQueryToPostgresETL:
    """ETL pipeline for BigQuery to PostgreSQL data synchronization."""

    def __init__(self, batch_size: int = 10000, max_workers: int = 4):
        """
        Initialize ETL pipeline.

        Args:
            batch_size: Number of records to process in each batch
            max_workers: Maximum concurrent workers for parallel processing
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.bigquery_client = BigQueryClient()
        self.postgres_manager = None
        self.redis_manager = RedisCacheManager()

        # ETL statistics
        self.stats = {
            "total_records": 0,
            "processed_records": 0,
            "failed_records": 0,
            "start_time": None,
            "end_time": None,
        }

    async def initialize(self) -> None:
        """Initialize database connections."""
        self.postgres_manager = await get_postgres_manager()
        logger.info("ETL pipeline initialized")

    async def sync_recent_data(
        self, hours_back: int = 24, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Sync recent data from BigQuery to PostgreSQL.

        Args:
            hours_back: Number of hours to sync
            force_refresh: Force refresh even if data exists

        Returns:
            ETL execution statistics
        """
        logger.info(f"Starting ETL sync for last {hours_back} hours")
        self.stats["start_time"] = datetime.now()

        try:
            # Create ETL job record
            job_id = await self.postgres_manager.log_etl_job(
                {
                    "job_name": f"bigquery_to_postgres_sync_{hours_back}h",
                    "job_type": "scheduled_sync",
                    "status": "running",
                    "started_at": self.stats["start_time"],
                    "metadata": {
                        "hours_back": hours_back,
                        "force_refresh": force_refresh,
                    },
                }
            )

            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)

            # Check if data already exists (unless force refresh)
            if not force_refresh:
                existing_count = await self._check_existing_data(start_time, end_time)
                if existing_count > 0:
                    logger.info(
                        f"Found {existing_count} existing records, skipping sync"
                    )
                    await self.postgres_manager.update_etl_job(
                        job_id,
                        {
                            "status": "completed",
                            "completed_at": datetime.now(),
                            "records_processed": 0,
                            "metadata": {
                                "skipped": True,
                                "existing_records": existing_count,
                            },
                        },
                    )
                    return self.stats

            # Sync node metadata first
            await self._sync_nodes()

            # Get all active nodes
            nodes = await self.postgres_manager.get_all_nodes()
            node_ids = [node["node_id"] for node in nodes]

            # Process nodes in parallel
            tasks = []
            for i in range(0, len(node_ids), self.max_workers):
                batch = node_ids[i : i + self.max_workers]
                for node_id in batch:
                    task = self._sync_node_data(node_id, start_time, end_time)
                    tasks.append(task)

                # Wait for batch to complete
                await asyncio.gather(*tasks)
                tasks = []

            # Final statistics
            self.stats["end_time"] = datetime.now()
            duration = (
                self.stats["end_time"] - self.stats["start_time"]
            ).total_seconds()

            # Update ETL job record
            await self.postgres_manager.update_etl_job(
                job_id,
                {
                    "status": "completed",
                    "completed_at": self.stats["end_time"],
                    "records_processed": self.stats["processed_records"],
                    "records_failed": self.stats["failed_records"],
                    "metadata": {
                        "duration_seconds": duration,
                        "records_per_second": self.stats["processed_records"] / duration
                        if duration > 0
                        else 0,
                    },
                },
            )

            logger.info(
                f"ETL sync completed: {self.stats['processed_records']} records in {duration:.2f}s"
            )

            # Refresh cache after sync
            await self._refresh_cache()

            return self.stats

        except Exception as e:
            logger.error(f"ETL sync failed: {e}")
            if "job_id" in locals():
                await self.postgres_manager.update_etl_job(
                    job_id,
                    {
                        "status": "failed",
                        "completed_at": datetime.now(),
                        "error_message": str(e),
                    },
                )
            raise

    async def sync_historical_data(
        self,
        start_date: datetime,
        end_date: datetime,
        node_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Sync historical data for specific date range.

        Args:
            start_date: Start date for sync
            end_date: End date for sync
            node_ids: Specific nodes to sync (None for all)

        Returns:
            ETL execution statistics
        """
        logger.info(f"Starting historical sync from {start_date} to {end_date}")
        self.stats["start_time"] = datetime.now()

        # If no specific nodes, get all
        if node_ids is None:
            nodes = await self.postgres_manager.get_all_nodes()
            node_ids = [node["node_id"] for node in nodes]

        # Process date range in daily chunks
        current_date = start_date
        while current_date < end_date:
            next_date = min(current_date + timedelta(days=1), end_date)

            logger.info(f"Processing {current_date.date()}")

            # Process all nodes for this date
            for node_id in node_ids:
                await self._sync_node_data(node_id, current_date, next_date)

            current_date = next_date

        self.stats["end_time"] = datetime.now()
        return self.stats

    async def _sync_nodes(self) -> None:
        """Sync node metadata from BigQuery to PostgreSQL."""
        logger.info("Syncing node metadata")

        query = f"""
        SELECT DISTINCT
            node_id,
            FIRST_VALUE(node_name) OVER (PARTITION BY node_id ORDER BY timestamp DESC) as node_name,
            FIRST_VALUE(node_type) OVER (PARTITION BY node_id ORDER BY timestamp DESC) as node_type,
            'Selargius' as location_name,
            true as is_active
        FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.sensor_readings_ml`
        WHERE node_id IS NOT NULL
        """

        df = self.bigquery_client.client.query(query).to_dataframe()

        for _, row in df.iterrows():
            node_data = {
                "node_id": row["node_id"],
                "node_name": row.get("node_name") or f"Node {row['node_id']}",
                "node_type": row.get("node_type") or "sensor",
                "location_name": row["location_name"],
                "is_active": row["is_active"],
            }
            await self.postgres_manager.upsert_node(node_data)

        logger.info(f"Synced {len(df)} nodes")

    async def _sync_node_data(
        self, node_id: str, start_time: datetime, end_time: datetime
    ) -> None:
        """Sync data for a specific node and time range."""
        try:
            # Query BigQuery
            query = f"""
            SELECT 
                timestamp,
                node_id,
                temperature,
                flow_rate,
                pressure,
                volume as total_flow,
                data_quality_score as quality_score
            FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.sensor_readings_ml`
            WHERE node_id = @node_id
            AND timestamp BETWEEN @start_time AND @end_time
            ORDER BY timestamp
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("node_id", "STRING", node_id),
                    bigquery.ScalarQueryParameter(
                        "start_time", "TIMESTAMP", start_time
                    ),
                    bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
                ]
            )

            df = self.bigquery_client.client.query(
                query, job_config=job_config
            ).to_dataframe()

            if df.empty:
                return

            # Process in batches
            for i in range(0, len(df), self.batch_size):
                batch_df = df.iloc[i : i + self.batch_size]

                # Convert to records
                readings = []
                for _, row in batch_df.iterrows():
                    reading = {
                        "timestamp": row["timestamp"].to_pydatetime(),
                        "node_id": row["node_id"],
                        "temperature": float(row["temperature"])
                        if pd.notna(row["temperature"])
                        else None,
                        "flow_rate": float(row["flow_rate"])
                        if pd.notna(row["flow_rate"])
                        else None,
                        "pressure": float(row["pressure"])
                        if pd.notna(row["pressure"])
                        else None,
                        "total_flow": float(row["total_flow"])
                        if pd.notna(row["total_flow"])
                        else None,
                        "quality_score": float(row["quality_score"])
                        if pd.notna(row["quality_score"])
                        else 1.0,
                    }
                    readings.append(reading)

                # Insert to PostgreSQL
                inserted = await self.postgres_manager.insert_sensor_readings_batch(
                    readings
                )
                self.stats["processed_records"] += inserted

            logger.info(f"Synced {len(df)} records for node {node_id}")

        except Exception as e:
            logger.error(f"Failed to sync node {node_id}: {e}")
            self.stats["failed_records"] += 1

    async def _check_existing_data(
        self, start_time: datetime, end_time: datetime
    ) -> int:
        """Check if data already exists in PostgreSQL."""
        async with self.postgres_manager.acquire() as conn:
            count = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM water_infrastructure.sensor_readings
                WHERE timestamp BETWEEN $1 AND $2
            """,
                start_time,
                end_time,
            )
            return count

    async def _refresh_cache(self) -> None:
        """Refresh Redis cache after ETL completion."""
        logger.info("Refreshing Redis cache")

        try:
            # Get latest readings for all nodes
            latest_readings = await self.postgres_manager.get_latest_readings()

            # Update Redis
            for node_id, reading in latest_readings.items():
                self.redis_manager.redis_client.hset(
                    f"node:{node_id}:latest",
                    mapping={
                        "timestamp": reading["timestamp"].isoformat(),
                        "flow_rate": reading.get("flow_rate", 0),
                        "pressure": reading.get("pressure", 0),
                        "temperature": reading.get("temperature", 0),
                    },
                )

            # Clear aggregated metrics to force recalculation
            for pattern in ["system:metrics:*", "node:*:metrics:*"]:
                keys = self.redis_manager.redis_client.keys(pattern)
                if keys:
                    self.redis_manager.redis_client.delete(*keys)

            logger.info("Cache refresh completed")

        except Exception as e:
            logger.error(f"Cache refresh failed: {e}")


async def run_daily_sync():
    """Run daily synchronization job."""
    etl = BigQueryToPostgresETL()
    await etl.initialize()

    # Sync last 24 hours
    stats = await etl.sync_recent_data(hours_back=24)

    # Log results
    logger.info(f"Daily sync completed: {stats}")


async def run_historical_sync(days_back: int = 90):
    """Run historical data synchronization."""
    etl = BigQueryToPostgresETL()
    await etl.initialize()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    stats = await etl.sync_historical_data(start_date, end_date)

    logger.info(f"Historical sync completed: {stats}")


if __name__ == "__main__":
    # Example: Run daily sync
    asyncio.run(run_daily_sync())

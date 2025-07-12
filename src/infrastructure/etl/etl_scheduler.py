"""
ETL Scheduler for automated data synchronization.

This module manages scheduled ETL jobs for the hybrid data architecture,
including daily syncs, cache refreshes, and ML model updates.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.infrastructure.cache.redis_cache_manager import RedisCacheManager
from src.infrastructure.database.postgres_manager import get_postgres_manager
from src.infrastructure.etl.bigquery_to_postgres_etl import BigQueryToPostgresETL

logger = logging.getLogger(__name__)


class ETLScheduler:
    """Manages scheduled ETL jobs and data synchronization tasks."""

    def __init__(self):
        """Initialize ETL scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.etl_pipeline = BigQueryToPostgresETL()
        self.redis_manager = RedisCacheManager()
        self.postgres_manager = None

        # Job tracking
        self.active_jobs = {}

        # Configure scheduler
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)

    async def initialize(self) -> None:
        """Initialize scheduler and connections."""
        logger.info("Initializing ETL scheduler")

        # Initialize connections
        await self.etl_pipeline.initialize()
        self.postgres_manager = await get_postgres_manager()

        # Schedule jobs
        self._schedule_jobs()

        # Start scheduler
        self.scheduler.start()
        logger.info("ETL scheduler started")

    def _schedule_jobs(self) -> None:
        """Schedule all ETL jobs."""

        # 1. Daily data sync (2 AM)
        self.scheduler.add_job(
            self._run_daily_sync,
            CronTrigger(hour=2, minute=0),
            id="daily_sync",
            name="Daily BigQuery to PostgreSQL sync",
            replace_existing=True,
        )

        # 2. Hourly cache refresh
        self.scheduler.add_job(
            self._refresh_cache,
            IntervalTrigger(hours=1),
            id="hourly_cache_refresh",
            name="Hourly cache refresh",
            replace_existing=True,
        )

        # 3. Real-time data sync (every 5 minutes)
        self.scheduler.add_job(
            self._sync_recent_data,
            IntervalTrigger(minutes=5),
            id="realtime_sync",
            name="Real-time data sync",
            replace_existing=True,
        )

        # 4. Anomaly detection (every 15 minutes)
        self.scheduler.add_job(
            self._run_anomaly_detection,
            IntervalTrigger(minutes=15),
            id="anomaly_detection",
            name="Anomaly detection",
            replace_existing=True,
        )

        # 5. Data quality check (daily at 6 AM)
        self.scheduler.add_job(
            self._run_data_quality_check,
            CronTrigger(hour=6, minute=0),
            id="data_quality_check",
            name="Daily data quality check",
            replace_existing=True,
        )

        # 6. Cleanup old data (weekly on Sunday at 3 AM)
        self.scheduler.add_job(
            self._cleanup_old_data,
            CronTrigger(day_of_week=6, hour=3, minute=0),
            id="weekly_cleanup",
            name="Weekly data cleanup",
            replace_existing=True,
        )

        logger.info(f"Scheduled {len(self.scheduler.get_jobs())} jobs")

    # ====================================
    # Scheduled Jobs
    # ====================================

    async def _run_daily_sync(self) -> None:
        """Run daily data synchronization."""
        logger.info("Starting daily sync job")
        job_start = datetime.now()

        try:
            # Log job start
            job_id = await self.postgres_manager.log_etl_job(
                {
                    "job_name": "daily_sync",
                    "job_type": "scheduled",
                    "status": "running",
                    "started_at": job_start,
                }
            )

            # Run sync for last 48 hours (with overlap)
            stats = await self.etl_pipeline.sync_recent_data(hours_back=48)

            # Update job status
            await self.postgres_manager.update_etl_job(
                job_id,
                {
                    "status": "completed",
                    "completed_at": datetime.now(),
                    "records_processed": stats["processed_records"],
                    "metadata": stats,
                },
            )

            logger.info(f"Daily sync completed: {stats['processed_records']} records")

        except Exception as e:
            logger.error(f"Daily sync failed: {e}")
            if "job_id" in locals():
                await self.postgres_manager.update_etl_job(
                    job_id,
                    {
                        "status": "failed",
                        "completed_at": datetime.now(),
                        "error_message": str(e),
                    },
                )

    async def _sync_recent_data(self) -> None:
        """Sync recent data (last hour)."""
        logger.debug("Starting real-time sync")

        try:
            # Sync last 2 hours (with overlap)
            stats = await self.etl_pipeline.sync_recent_data(hours_back=2)

            if stats["processed_records"] > 0:
                logger.info(f"Real-time sync: {stats['processed_records']} new records")

        except Exception as e:
            logger.error(f"Real-time sync failed: {e}")

    async def _refresh_cache(self) -> None:
        """Refresh Redis cache from PostgreSQL."""
        logger.debug("Refreshing cache")

        try:
            # Get system metrics for all time ranges
            time_ranges = ["1h", "6h", "24h", "3d", "7d", "30d"]

            for time_range in time_ranges:
                metrics = await self.postgres_manager.get_system_metrics(time_range)

                # Cache in Redis
                self.redis_manager.redis_client.setex(
                    f"system:metrics:{time_range}", 3600, str(metrics)  # 1 hour TTL
                )

            # Refresh latest readings
            latest_readings = await self.postgres_manager.get_latest_readings()

            for node_id, reading in latest_readings.items():
                self.redis_manager.redis_client.hset(
                    f"node:{node_id}:latest",
                    mapping={
                        "timestamp": reading["timestamp"].isoformat(),
                        "flow_rate": str(reading.get("flow_rate", 0)),
                        "pressure": str(reading.get("pressure", 0)),
                        "temperature": str(reading.get("temperature", 0)),
                    },
                )

            logger.debug("Cache refresh completed")

        except Exception as e:
            logger.error(f"Cache refresh failed: {e}")

    async def _run_anomaly_detection(self) -> None:
        """Run anomaly detection on recent data."""
        logger.debug("Running anomaly detection")

        try:
            # Get recent data from PostgreSQL
            nodes = await self.postgres_manager.get_all_nodes()

            for node in nodes:
                node_id = node["node_id"]

                # Get last hour of data
                async with self.postgres_manager.acquire() as conn:
                    rows = await conn.fetch(
                        """
                        SELECT 
                            timestamp, flow_rate, pressure, temperature
                        FROM water_infrastructure.sensor_readings
                        WHERE node_id = $1
                        AND timestamp > CURRENT_TIMESTAMP - INTERVAL '1 hour'
                        ORDER BY timestamp
                    """,
                        node_id,
                    )

                    if len(rows) < 10:
                        continue

                    # Calculate statistics
                    flow_rates = [
                        r["flow_rate"] for r in rows if r["flow_rate"] is not None
                    ]

                    if flow_rates:
                        avg_flow = sum(flow_rates) / len(flow_rates)
                        std_flow = (
                            sum((x - avg_flow) ** 2 for x in flow_rates)
                            / len(flow_rates)
                        ) ** 0.5

                        # Check latest reading for anomalies
                        latest = rows[-1]
                        if latest["flow_rate"] is not None:
                            deviation = abs(latest["flow_rate"] - avg_flow)

                            if deviation > 3 * std_flow and std_flow > 0:
                                # Record anomaly
                                anomaly = {
                                    "timestamp": latest["timestamp"],
                                    "node_id": node_id,
                                    "anomaly_type": "flow_anomaly",
                                    "severity": "warning"
                                    if deviation < 4 * std_flow
                                    else "critical",
                                    "measurement_type": "flow_rate",
                                    "actual_value": latest["flow_rate"],
                                    "expected_value": avg_flow,
                                    "deviation_percentage": (deviation / avg_flow * 100)
                                    if avg_flow > 0
                                    else 0,
                                    "detection_method": "statistical_3sigma",
                                }

                                await self.postgres_manager.insert_anomaly(anomaly)
                                logger.info(
                                    f"Anomaly detected: {node_id} - {anomaly['anomaly_type']}"
                                )

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")

    async def _run_data_quality_check(self) -> None:
        """Run data quality checks."""
        logger.info("Running data quality check")

        try:
            async with self.postgres_manager.acquire() as conn:
                # Check for missing data
                missing_data = await conn.fetch(
                    """
                    WITH expected_readings AS (
                        SELECT 
                            n.node_id,
                            generate_series(
                                CURRENT_TIMESTAMP - INTERVAL '24 hours',
                                CURRENT_TIMESTAMP,
                                INTERVAL '30 minutes'
                            ) as expected_time
                        FROM water_infrastructure.nodes n
                        WHERE n.is_active = true
                    ),
                    actual_readings AS (
                        SELECT DISTINCT
                            node_id,
                            date_trunc('hour', timestamp) + 
                            INTERVAL '30 minutes' * FLOOR(EXTRACT(MINUTE FROM timestamp) / 30) as reading_time
                        FROM water_infrastructure.sensor_readings
                        WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                    )
                    SELECT 
                        e.node_id,
                        COUNT(*) as missing_readings
                    FROM expected_readings e
                    LEFT JOIN actual_readings a 
                        ON e.node_id = a.node_id 
                        AND e.expected_time = a.reading_time
                    WHERE a.reading_time IS NULL
                    GROUP BY e.node_id
                    HAVING COUNT(*) > 5
                """
                )

                if missing_data:
                    logger.warning(f"Found {len(missing_data)} nodes with missing data")

                # Check for suspicious values
                suspicious = await conn.fetch(
                    """
                    SELECT 
                        node_id,
                        COUNT(*) as suspicious_readings
                    FROM water_infrastructure.sensor_readings
                    WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                    AND (
                        flow_rate < 0 OR flow_rate > 1000 OR
                        pressure < 0 OR pressure > 20 OR
                        temperature < -10 OR temperature > 60
                    )
                    GROUP BY node_id
                """
                )

                if suspicious:
                    logger.warning(
                        f"Found {len(suspicious)} nodes with suspicious readings"
                    )

                # Log quality check results
                await self.postgres_manager.log_etl_job(
                    {
                        "job_name": "data_quality_check",
                        "job_type": "quality_check",
                        "status": "completed",
                        "started_at": datetime.now(),
                        "completed_at": datetime.now(),
                        "metadata": {
                            "nodes_with_missing_data": len(missing_data),
                            "nodes_with_suspicious_data": len(suspicious),
                        },
                    }
                )

        except Exception as e:
            logger.error(f"Data quality check failed: {e}")

    async def _cleanup_old_data(self) -> None:
        """Clean up old data according to retention policies."""
        logger.info("Running data cleanup")

        try:
            async with self.postgres_manager.acquire() as conn:
                # Note: TimescaleDB retention policies handle most cleanup automatically
                # This is for additional cleanup tasks

                # Clean up old ETL job logs (keep 30 days)
                deleted = await conn.execute(
                    """
                    DELETE FROM water_infrastructure.etl_jobs
                    WHERE started_at < CURRENT_TIMESTAMP - INTERVAL '30 days'
                """
                )

                logger.info(f"Deleted {deleted} old ETL job records")

                # Clean up resolved anomalies (keep 90 days)
                deleted = await conn.execute(
                    """
                    DELETE FROM water_infrastructure.anomalies
                    WHERE resolved_at IS NOT NULL
                    AND resolved_at < CURRENT_TIMESTAMP - INTERVAL '90 days'
                """
                )

                logger.info(f"Deleted {deleted} old resolved anomalies")

                # Vacuum analyze for performance
                await conn.execute(
                    "VACUUM ANALYZE water_infrastructure.sensor_readings"
                )

        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")

    # ====================================
    # Event Handlers
    # ====================================

    def _job_executed(self, event) -> None:
        """Handle successful job execution."""
        job_id = event.job_id
        logger.debug(f"Job {job_id} executed successfully")

    def _job_error(self, event) -> None:
        """Handle job execution error."""
        job_id = event.job_id
        logger.error(f"Job {job_id} failed: {event.exception}")

    # ====================================
    # Management Methods
    # ====================================

    def get_job_status(self) -> Dict[str, Any]:
        """Get status of all scheduled jobs."""
        jobs = []

        for job in self.scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat()
                    if job.next_run_time
                    else None,
                    "trigger": str(job.trigger),
                }
            )

        return {"scheduler_running": self.scheduler.running, "jobs": jobs}

    def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job."""
        job = self.scheduler.get_job(job_id)
        if job:
            job.pause()
            logger.info(f"Paused job: {job_id}")
            return True
        return False

    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job."""
        job = self.scheduler.get_job(job_id)
        if job:
            job.resume()
            logger.info(f"Resumed job: {job_id}")
            return True
        return False

    def trigger_job(self, job_id: str) -> bool:
        """Manually trigger a job."""
        job = self.scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"Manually triggered job: {job_id}")
            return True
        return False

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("ETL scheduler shutdown")


# Singleton instance
_etl_scheduler: Optional[ETLScheduler] = None


async def get_etl_scheduler() -> ETLScheduler:
    """Get or create ETL scheduler singleton."""
    global _etl_scheduler
    if _etl_scheduler is None:
        _etl_scheduler = ETLScheduler()
        await _etl_scheduler.initialize()
    return _etl_scheduler


if __name__ == "__main__":
    # Run scheduler standalone
    async def main():
        scheduler = await get_etl_scheduler()

        # Keep running
        try:
            while True:
                await asyncio.sleep(60)
                # Print status every minute
                status = scheduler.get_job_status()
                logger.info(f"Scheduler status: {status}")
        except KeyboardInterrupt:
            scheduler.shutdown()

    asyncio.run(main())

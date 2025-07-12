"""
Main entry point for the processing service.

This service runs continuously and:
1. Checks BigQuery for new data every 30 minutes
2. Processes data using multi-threading
3. Stores computed results in PostgreSQL
4. Manages ML model training and deployment
"""

import asyncio
import logging
import os
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional

from google.cloud import bigquery

from src.infrastructure.bigquery.bigquery_client import BigQueryClient
from src.infrastructure.database.postgres_manager import get_postgres_manager
from src.processing.service.data_processor import DataProcessor
from src.processing.service.ml_manager import MLModelManager
from src.processing.service.scheduler import ProcessingScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/app/logs/processing_service.log"),
    ],
)
logger = logging.getLogger(__name__)


class ProcessingService:
    """Main processing service that orchestrates all background tasks."""

    def __init__(self):
        """Initialize the processing service."""
        self.running = False
        self.data_processor = DataProcessor()
        self.ml_manager = MLModelManager()
        self.scheduler = ProcessingScheduler()
        self.bigquery_client = BigQueryClient()
        self.postgres_manager = None

        # Processing configuration
        self.check_interval_minutes = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))
        self.last_processed_timestamp = None

    async def initialize(self):
        """Initialize all components."""
        logger.info("Initializing processing service...")

        # Initialize database connections
        self.postgres_manager = await get_postgres_manager()

        # Initialize components
        await self.data_processor.initialize(
            self.postgres_manager, self.bigquery_client
        )
        await self.ml_manager.initialize(self.postgres_manager, self.bigquery_client)
        await self.scheduler.initialize()

        # Get last processed timestamp
        self.last_processed_timestamp = await self._get_last_processed_timestamp()

        logger.info("Processing service initialized successfully")

    async def start(self):
        """Start the processing service."""
        logger.info("Starting processing service...")
        self.running = True

        # Schedule regular tasks
        self._schedule_tasks()

        # Main processing loop
        while self.running:
            try:
                await self._process_cycle()

                # Wait for next cycle
                await asyncio.sleep(self.check_interval_minutes * 60)

            except Exception as e:
                logger.error(f"Error in processing cycle: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute before retry

    async def stop(self):
        """Stop the processing service gracefully."""
        logger.info("Stopping processing service...")
        self.running = False

        # Stop scheduler
        await self.scheduler.stop()

        # Close database connections
        if self.postgres_manager:
            await self.postgres_manager.close()

        logger.info("Processing service stopped")

    def _schedule_tasks(self):
        """Schedule recurring tasks."""
        # Data processing every 30 minutes
        self.scheduler.add_job(
            self._process_cycle,
            "interval",
            minutes=self.check_interval_minutes,
            id="data_processing",
            name="Data Processing Cycle",
        )

        # ML model evaluation daily at 2 AM
        self.scheduler.add_job(
            self.ml_manager.evaluate_models,
            "cron",
            hour=2,
            minute=0,
            id="model_evaluation",
            name="ML Model Evaluation",
        )

        # Weekly model retraining on Sundays at 3 AM
        self.scheduler.add_job(
            self.ml_manager.retrain_models,
            "cron",
            day_of_week=0,
            hour=3,
            minute=0,
            id="model_retraining",
            name="ML Model Retraining",
        )

        # Data quality check every 6 hours
        self.scheduler.add_job(
            self.data_processor.check_data_quality,
            "interval",
            hours=6,
            id="data_quality_check",
            name="Data Quality Check",
        )

    async def _process_cycle(self):
        """Main processing cycle."""
        logger.info("Starting processing cycle...")

        # Create processing job
        job_id = await self._create_processing_job()

        try:
            # 1. Check for new data in BigQuery
            new_data_info = await self._check_for_new_data()

            if not new_data_info["has_new_data"]:
                logger.info("No new data found, skipping processing")
                await self._update_job_status(
                    job_id, "completed", {"message": "No new data to process"}
                )
                return

            logger.info(
                f"Found new data: {new_data_info['record_count']} records from "
                f"{new_data_info['min_timestamp']} to {new_data_info['max_timestamp']}"
            )

            # 2. Process new data
            processing_results = await self.data_processor.process_new_data(
                start_timestamp=new_data_info["min_timestamp"],
                end_timestamp=new_data_info["max_timestamp"],
                job_id=job_id,
            )

            # 3. Update last processed timestamp
            self.last_processed_timestamp = new_data_info["max_timestamp"]
            await self._save_last_processed_timestamp(self.last_processed_timestamp)

            # 4. Trigger ML predictions if needed
            if processing_results["success"]:
                await self.ml_manager.generate_predictions(
                    nodes=processing_results["processed_nodes"],
                    timestamp=new_data_info["max_timestamp"],
                )

            # 5. Update job status
            await self._update_job_status(job_id, "completed", processing_results)

            logger.info(
                f"Processing cycle completed successfully. Processed {processing_results['total_records']} records"
            )

        except Exception as e:
            logger.error(f"Processing cycle failed: {e}", exc_info=True)
            await self._update_job_status(job_id, "failed", {"error": str(e)})
            raise

    async def _check_for_new_data(self) -> dict:
        """Check BigQuery for new data since last processed timestamp."""
        # Check if BigQuery client is available
        if not self.bigquery_client or not self.bigquery_client.client:
            logger.error("BigQuery client not available - skipping data check")
            return {
                "has_new_data": False,
                "record_count": 0,
                "min_timestamp": None,
                "max_timestamp": None,
            }

        query = """
        SELECT
            COUNT(*) as record_count,
            MIN(timestamp) as min_timestamp,
            MAX(timestamp) as max_timestamp
        FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.sensor_readings_ml`
        WHERE timestamp > @last_timestamp
        """

        job_config = bigquery.QueryJobConfig()
        job_config.query_parameters = [
            bigquery.ScalarQueryParameter(
                "last_timestamp",
                "TIMESTAMP",
                self.last_processed_timestamp or datetime.now() - timedelta(days=1),
            )
        ]

        result = self.bigquery_client.client.query(
            query, job_config=job_config
        ).result()
        row = list(result)[0]

        return {
            "has_new_data": row.record_count > 0,
            "record_count": row.record_count,
            "min_timestamp": row.min_timestamp,
            "max_timestamp": row.max_timestamp,
        }

    async def _get_last_processed_timestamp(self) -> Optional[datetime]:
        """Get the last processed timestamp from database."""
        async with self.postgres_manager.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT MAX(window_end)
                FROM water_infrastructure.computed_metrics
            """
            )
            return result

    async def _save_last_processed_timestamp(self, timestamp: datetime):
        """Save the last processed timestamp."""
        # This could be stored in a dedicated table or Redis
        # For now, we rely on the computed_metrics table
        pass

    async def _create_processing_job(self) -> str:
        """Create a new processing job record."""
        async with self.postgres_manager.acquire() as conn:
            job_id = await conn.fetchval(
                """
                INSERT INTO water_infrastructure.processing_jobs
                (job_type, job_name, status, triggered_by)
                VALUES ('data_processing', 'Scheduled data processing', 'running', 'scheduler')
                RETURNING job_id
            """
            )
            return str(job_id)

    async def _update_job_status(self, job_id: str, status: str, result: dict):
        """Update processing job status."""
        import json

        async with self.postgres_manager.acquire() as conn:
            await conn.execute(
                """
                UPDATE water_infrastructure.processing_jobs
                SET
                    status = $1,
                    completed_at = CURRENT_TIMESTAMP,
                    duration_seconds = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - started_at)),
                    result_summary = $2
                WHERE job_id = $3
            """,
                status,
                json.dumps(result),
                job_id,
            )


def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(service.stop())


async def main():
    """Main entry point."""
    global service

    # Create service instance
    service = ProcessingService()

    # Setup signal handlers
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        # Initialize service
        await service.initialize()

        # Start service
        await service.start()

    except Exception as e:
        logger.error(f"Service failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

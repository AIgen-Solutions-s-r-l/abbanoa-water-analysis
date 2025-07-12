"""
Processing scheduler using APScheduler.

Manages scheduled tasks for the processing service.
"""

import logging

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


class ProcessingScheduler:
    """Manages scheduled processing tasks."""

    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = None

    async def initialize(self):
        """Initialize the scheduler."""
        jobstores = {"default": MemoryJobStore()}

        executors = {"default": AsyncIOExecutor()}

        job_defaults = {
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 300,  # 5 minutes
        }

        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone="UTC",
        )

        self.scheduler.start()
        logger.info("Processing scheduler initialized and started")

    def add_job(self, func, trigger, **kwargs):
        """Add a job to the scheduler."""
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")

        job = self.scheduler.add_job(func, trigger, **kwargs)
        logger.info(f"Added job: {kwargs.get('name', 'unnamed')} with ID: {job.id}")
        return job

    def remove_job(self, job_id: str):
        """Remove a job from the scheduler."""
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")

        self.scheduler.remove_job(job_id)
        logger.info(f"Removed job: {job_id}")

    def pause_job(self, job_id: str):
        """Pause a scheduled job."""
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")

        self.scheduler.pause_job(job_id)
        logger.info(f"Paused job: {job_id}")

    def resume_job(self, job_id: str):
        """Resume a paused job."""
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")

        self.scheduler.resume_job(job_id)
        logger.info(f"Resumed job: {job_id}")

    def get_jobs(self):
        """Get all scheduled jobs."""
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")

        return self.scheduler.get_jobs()

    async def stop(self):
        """Stop the scheduler."""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Processing scheduler stopped")

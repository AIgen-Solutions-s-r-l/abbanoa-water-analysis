"""
Cache initialization script for water infrastructure dashboard.

This script pre-loads and processes all data from BigQuery into Redis
for fast dashboard access. It should be run on application startup.
"""

import logging
import os
import threading
import time
from datetime import datetime

import schedule

from .redis_cache_manager import RedisCacheManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CacheInitializer:
    """Handles cache initialization and refresh scheduling."""

    def __init__(self):
        """Initialize cache manager with environment settings."""
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.cache_ttl_hours = int(os.getenv("CACHE_TTL_HOURS", 24))
        self.refresh_interval_hours = int(os.getenv("CACHE_REFRESH_HOURS", 6))

        self.cache_manager = RedisCacheManager(
            redis_host=self.redis_host,
            redis_port=self.redis_port,
            redis_db=self.redis_db,
            ttl_hours=self.cache_ttl_hours,
        )

        self.is_running = False
        self.refresh_thread = None

    def start(self, force_refresh: bool = False) -> None:
        """Start cache initialization and schedule periodic refreshes."""
        logger.info("Starting cache initialization...")
        start_time = time.time()

        try:
            # Initialize cache
            self.cache_manager.initialize_cache(force_refresh=force_refresh)

            # Schedule periodic refresh
            self._schedule_refresh()

            # Start background thread for scheduled jobs
            self.is_running = True
            self.refresh_thread = threading.Thread(
                target=self._run_scheduler, daemon=True
            )
            self.refresh_thread.start()

            elapsed = time.time() - start_time
            logger.info(f"Cache initialization completed in {elapsed:.2f} seconds")

        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            raise

    def stop(self) -> None:
        """Stop the cache refresh scheduler."""
        self.is_running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=5)
        logger.info("Cache refresh scheduler stopped")

    def _schedule_refresh(self) -> None:
        """Schedule periodic cache refreshes."""
        # Schedule refresh every N hours
        schedule.every(self.refresh_interval_hours).hours.do(self._refresh_cache)

        # Also schedule a daily full refresh at 2 AM
        schedule.every().day.at("02:00").do(
            lambda: self._refresh_cache(full_refresh=True)
        )

        logger.info(
            f"Scheduled cache refresh every {self.refresh_interval_hours} hours"
        )

    def _refresh_cache(self, full_refresh: bool = False) -> None:
        """Refresh cache data."""
        logger.info(f"Starting cache refresh (full_refresh={full_refresh})...")
        start_time = time.time()

        try:
            self.cache_manager.initialize_cache(force_refresh=True)
            elapsed = time.time() - start_time
            logger.info(f"Cache refresh completed in {elapsed:.2f} seconds")
        except Exception as e:
            logger.error(f"Cache refresh failed: {e}")

    def _run_scheduler(self) -> None:
        """Run the scheduler in a background thread."""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        try:
            info = self.cache_manager.redis_client.info()
            dbsize = self.cache_manager.redis_client.dbsize()

            return {
                "status": "connected",
                "keys": dbsize,
                "memory_used": info.get("used_memory_human", "N/A"),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "last_refresh": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Singleton instance
_initializer = None


def get_cache_initializer() -> CacheInitializer:
    """Get or create the cache initializer singleton."""
    global _initializer
    if _initializer is None:
        _initializer = CacheInitializer()
    return _initializer


def initialize_cache_on_startup(force_refresh: bool = False) -> None:
    """Initialize cache on application startup."""
    initializer = get_cache_initializer()
    initializer.start(force_refresh=force_refresh)


def get_cache_manager() -> RedisCacheManager:
    """Get the cache manager instance."""
    initializer = get_cache_initializer()
    return initializer.cache_manager


if __name__ == "__main__":
    # Run cache initialization
    logger.info("Running cache initialization...")
    initialize_cache_on_startup(force_refresh=True)

    # Keep running for scheduled refreshes
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Stopping cache initializer...")
        get_cache_initializer().stop()

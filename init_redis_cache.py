#!/usr/bin/env python3
"""
Initialize Redis cache for the Abbanoa dashboard.

This script loads all data from BigQuery into Redis for fast dashboard access.
Run this before starting the Streamlit dashboard.
"""

import sys
import os
import logging
import argparse
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.cache.cache_initializer import (
    initialize_cache_on_startup,
    get_cache_initializer,
    get_cache_manager,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main function to initialize Redis cache."""
    parser = argparse.ArgumentParser(
        description="Initialize Redis cache for Abbanoa dashboard"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force refresh even if cache exists"
    )
    parser.add_argument(
        "--redis-host", default="localhost", help="Redis host (default: localhost)"
    )
    parser.add_argument(
        "--redis-port", type=int, default=6379, help="Redis port (default: 6379)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show cache statistics after initialization",
    )

    args = parser.parse_args()

    # Set environment variables
    os.environ["REDIS_HOST"] = args.redis_host
    os.environ["REDIS_PORT"] = str(args.redis_port)

    try:
        logger.info("=" * 60)
        logger.info("Abbanoa Dashboard - Redis Cache Initialization")
        logger.info("=" * 60)
        logger.info(f"Redis host: {args.redis_host}:{args.redis_port}")
        logger.info(f"Force refresh: {args.force}")
        logger.info("")

        # Check Redis connection
        cache_manager = get_cache_manager()
        try:
            cache_manager.redis_client.ping()
            logger.info("✅ Redis connection successful")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            logger.error("Make sure Redis is running on the specified host and port")
            return 1

        # Initialize cache
        logger.info("Starting cache initialization...")
        start_time = datetime.now()

        initialize_cache_on_startup(force_refresh=args.force)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Cache initialization completed in {elapsed:.2f} seconds")

        # Show statistics if requested
        if args.stats:
            logger.info("")
            logger.info("Cache Statistics:")
            logger.info("-" * 40)

            initializer = get_cache_initializer()
            stats = initializer.get_cache_stats()

            logger.info(f"Status: {stats['status']}")
            logger.info(f"Total keys: {stats.get('keys', 0)}")
            logger.info(f"Memory used: {stats.get('memory_used', 'N/A')}")

            # Show sample data
            all_nodes = cache_manager.redis_client.lrange("nodes:all", 0, -1)
            logger.info(f"Cached nodes: {len(all_nodes)}")

            if all_nodes:
                # Show sample node data
                sample_node = all_nodes[0]
                latest = cache_manager.get_latest_reading(sample_node)
                if latest:
                    logger.info(f"\nSample data for node {sample_node}:")
                    logger.info(f"  Latest flow: {latest.get('flow_rate', 0):.2f} L/s")
                    logger.info(
                        f"  Latest pressure: {latest.get('pressure', 0):.2f} bar"
                    )

            # Show anomaly count
            anomalies = cache_manager.get_recent_anomalies(limit=1000)
            logger.info(f"\nCached anomalies: {len(anomalies)}")

        logger.info("")
        logger.info("✅ Redis cache is ready for use!")
        logger.info("You can now start the Streamlit dashboard.")

        return 0

    except Exception as e:
        logger.error(f"❌ Cache initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

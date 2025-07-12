#!/usr/bin/env python3
"""
Force initial processing of all available data in BigQuery.
This script is useful for the first run when there's no processing history.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processing.service.main import ProcessingService
from src.infrastructure.database.postgres_manager import get_postgres_manager


async def force_initial_processing():
    """Force processing of all available data."""
    print("=== Forcing Initial Data Processing ===")

    # Initialize processing service
    service = ProcessingService()
    await service.initialize()

    # Override last processed timestamp to process all data
    service.last_processed_timestamp = datetime(
        2024, 1, 1
    )  # Start from beginning of 2024

    print(f"Set last processed timestamp to: {service.last_processed_timestamp}")
    print("Starting processing cycle...")

    try:
        # Run one processing cycle
        await service._process_cycle()
        print("Processing cycle completed!")

        # Check results
        postgres_manager = await get_postgres_manager()
        async with postgres_manager.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM water_infrastructure.computed_metrics"
            )
            print(f"Computed metrics created: {count}")

            count = await conn.fetchval(
                "SELECT COUNT(*) FROM water_infrastructure.sensor_readings"
            )
            print(f"Sensor readings stored: {count}")

    except Exception as e:
        print(f"Error during processing: {e}")
        raise
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(force_initial_processing())

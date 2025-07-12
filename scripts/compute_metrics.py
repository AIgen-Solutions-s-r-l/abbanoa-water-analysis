#!/usr/bin/env python3
"""
Compute metrics from sensor_readings data.
"""

import asyncio
import sys
from datetime import datetime, timedelta
import logging

# Add project root to path
sys.path.append("/home/alessio/Customers/Abbanoa")

from src.infrastructure.database.postgres_manager import get_postgres_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def compute_metrics():
    """Compute and insert computed metrics from sensor readings."""
    logger.info("Starting metrics computation")

    postgres_manager = await get_postgres_manager()

    async with postgres_manager.acquire() as conn:
        # Get date range of sensor data
        date_range = await conn.fetchrow(
            """
            SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date
            FROM water_infrastructure.sensor_readings
        """
        )

        if not date_range["min_date"]:
            logger.error("No sensor data found")
            return

        logger.info(
            f"Computing metrics for data from {date_range['min_date']} to {date_range['max_date']}"
        )

        # Compute hourly metrics
        result = await conn.execute(
            """
            INSERT INTO water_infrastructure.computed_metrics (
                timestamp, node_id, metric_type, 
                value, aggregation_type, time_window,
                metadata
            )
            SELECT 
                date_trunc('hour', timestamp) as hour,
                node_id,
                'flow_rate' as metric_type,
                AVG(flow_rate) as value,
                'average' as aggregation_type,
                'hourly' as time_window,
                jsonb_build_object(
                    'count', COUNT(*),
                    'min', MIN(flow_rate),
                    'max', MAX(flow_rate),
                    'stddev', STDDEV(flow_rate)
                ) as metadata
            FROM water_infrastructure.sensor_readings
            WHERE flow_rate IS NOT NULL
            GROUP BY date_trunc('hour', timestamp), node_id
            
            UNION ALL
            
            SELECT 
                date_trunc('hour', timestamp) as hour,
                node_id,
                'pressure' as metric_type,
                AVG(pressure) as value,
                'average' as aggregation_type,
                'hourly' as time_window,
                jsonb_build_object(
                    'count', COUNT(*),
                    'min', MIN(pressure),
                    'max', MAX(pressure),
                    'stddev', STDDEV(pressure)
                ) as metadata
            FROM water_infrastructure.sensor_readings
            WHERE pressure IS NOT NULL
            GROUP BY date_trunc('hour', timestamp), node_id
            
            UNION ALL
            
            SELECT 
                date_trunc('hour', timestamp) as hour,
                node_id,
                'temperature' as metric_type,
                AVG(temperature) as value,
                'average' as aggregation_type,
                'hourly' as time_window,
                jsonb_build_object(
                    'count', COUNT(*),
                    'min', MIN(temperature),
                    'max', MAX(temperature)
                ) as metadata
            FROM water_infrastructure.sensor_readings
            WHERE temperature IS NOT NULL
            GROUP BY date_trunc('hour', timestamp), node_id
        """
        )

        logger.info("Computed hourly metrics")

        # Update system cache
        await conn.execute(
            """
            INSERT INTO water_infrastructure.system_heartbeat (component_name, last_heartbeat, status, metadata)
            VALUES ('metrics_computation', NOW(), 'healthy', jsonb_build_object('last_computation', NOW()))
            ON CONFLICT (component_name) DO UPDATE
            SET last_heartbeat = NOW(), status = 'healthy', metadata = jsonb_build_object('last_computation', NOW())
        """
        )

        # Get count of computed metrics
        count = await conn.fetchval(
            """
            SELECT COUNT(*) FROM water_infrastructure.computed_metrics
        """
        )

        logger.info(f"Total computed metrics: {count}")


async def main():
    """Main function."""
    try:
        await compute_metrics()
        logger.info("✅ Metrics computation completed successfully!")
    except Exception as e:
        logger.error(f"❌ Computation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

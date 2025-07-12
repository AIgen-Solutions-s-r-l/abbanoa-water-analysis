#!/usr/bin/env python3
"""
Load test data into the hybrid architecture for immediate display.
"""

import os
import asyncio
from datetime import datetime, timedelta
import random

# Set environment
os.environ["POSTGRES_PASSWORD"] = "postgres"


async def load_test_data():
    """Load test data into PostgreSQL and Redis for immediate display."""
    print("Loading test data into hybrid architecture...")

    from src.infrastructure.database.postgres_manager import get_postgres_manager
    from src.infrastructure.cache.redis_cache_manager import RedisCacheManager

    # Initialize managers
    postgres = await get_postgres_manager()
    redis_manager = RedisCacheManager()

    # Define nodes (matching the overview tab expectations)
    nodes = [
        {"id": "PRIMARY_STATION", "name": "Primary Station"},
        {"id": "SECONDARY_STATION", "name": "Secondary Station"},
        {"id": "DISTRIBUTION_A", "name": "Distribution A"},
        {"id": "DISTRIBUTION_B", "name": "Distribution B"},
        {"id": "PRESSURE_ZONE_1", "name": "Pressure Zone 1"},
        {"id": "PRESSURE_ZONE_2", "name": "Pressure Zone 2"},
        {"id": "RESERVOIR_EAST", "name": "Reservoir East"},
        {"id": "RESERVOIR_WEST", "name": "Reservoir West"},
        {"id": "PUMP_STATION_1", "name": "Pump Station 1"},
    ]

    # Insert nodes
    for node in nodes:
        await postgres.upsert_node(
            {
                "node_id": node["id"],
                "node_name": node["name"],
                "node_type": "sensor",
                "location_name": "Selargius",
                "is_active": True,
                "metadata": {"source": "test_data"},
            }
        )

    print(f"✅ Inserted {len(nodes)} nodes")

    # Generate recent sensor data (last 24 hours)
    now = datetime.now()
    readings = []

    for hours_ago in range(24, -1, -1):  # 24 hours ago to now
        timestamp = now - timedelta(hours=hours_ago)

        for node in nodes:
            # Generate realistic values
            base_flow = 100 + random.uniform(-20, 20)
            base_pressure = 4.5 + random.uniform(-0.5, 0.5)
            base_temp = 15 + random.uniform(-2, 2)

            readings.append(
                {
                    "timestamp": timestamp,
                    "node_id": node["id"],
                    "temperature": base_temp,
                    "flow_rate": base_flow,
                    "pressure": base_pressure,
                    "total_flow": base_flow * 3600,  # hourly volume
                    "quality_score": 0.95 + random.uniform(0, 0.05),
                }
            )

    # Insert batch to PostgreSQL
    count = await postgres.insert_sensor_readings_batch(readings)
    print(f"✅ Inserted {count} sensor readings")

    # Update Redis with latest values
    for node in nodes:
        latest_reading = readings[-len(nodes) + nodes.index(node)]

        # Store in Redis
        redis_manager.redis_client.hset(
            f"node:{node['id']}:latest",
            mapping={
                "timestamp": latest_reading["timestamp"].isoformat(),
                "flow_rate": str(latest_reading["flow_rate"]),
                "pressure": str(latest_reading["pressure"]),
                "temperature": str(latest_reading["temperature"]),
            },
        )

        # Also store in metrics format
        redis_manager.redis_client.hset(
            f"node:{node['id']}:metrics:24h",
            mapping={
                "avg_flow": str(latest_reading["flow_rate"]),
                "avg_pressure": str(latest_reading["pressure"]),
                "total_volume": str(latest_reading["flow_rate"] * 24 * 3600),
                "efficiency": "95.5",
            },
        )

    # Store system metrics
    total_flow = sum(r["flow_rate"] for r in readings[-len(nodes) :])
    avg_pressure = sum(r["pressure"] for r in readings[-len(nodes) :]) / len(nodes)

    redis_manager.redis_client.hset(
        "system:metrics:24h",
        mapping={
            "total_flow": str(total_flow),
            "avg_pressure": str(avg_pressure),
            "active_nodes": str(len(nodes)),
            "total_volume": str(total_flow * 24 * 3600),
            "anomaly_count": "0",
        },
    )

    print("✅ Updated Redis cache")

    # Get system metrics from PostgreSQL
    metrics = await postgres.get_system_metrics("24h")
    print("\n📊 System Metrics:")
    print(f"  Active Nodes: {metrics.get('active_nodes', 0)}")
    print(f"  Average Pressure: {metrics.get('avg_pressure', 0):.2f} bar")
    print(f"  Total Flow: {metrics.get('total_flow', 0):.2f} L/s")

    print("\n✅ Test data loaded successfully!")
    print("🔄 Please refresh the dashboard to see the data")


if __name__ == "__main__":
    asyncio.run(load_test_data())

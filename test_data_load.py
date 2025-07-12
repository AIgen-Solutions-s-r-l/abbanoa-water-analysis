#!/usr/bin/env python3
"""
Simple test to load some data into the hybrid architecture.
"""

import asyncio
import os
from datetime import datetime, timedelta
from google.cloud import bigquery

# Set environment
os.environ["POSTGRES_PASSWORD"] = "postgres"


async def test_data_load():
    """Test loading data from BigQuery."""
    print("🔍 Checking BigQuery data...")

    # Connect to BigQuery
    client = bigquery.Client(project="abbanoa-464816", location="EU")

    # Check what nodes we have
    query = """
    SELECT DISTINCT node_id, COUNT(*) as count
    FROM `abbanoa-464816.water_infrastructure.sensor_readings`
    WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    GROUP BY node_id
    ORDER BY count DESC
    LIMIT 10
    """

    print("\nNodes with recent data:")
    results = client.query(query).result()
    nodes = []
    for row in results:
        print(f"  Node: {row.node_id} - Records: {row.count}")
        nodes.append(row.node_id)

    if not nodes:
        print("\n❌ No recent data found in BigQuery!")
        return

    # Now let's manually insert some data into PostgreSQL
    print("\n📥 Loading sample data into PostgreSQL...")

    from src.infrastructure.database.postgres_manager import get_postgres_manager

    postgres = await get_postgres_manager()

    # Insert a test node
    test_node = nodes[0] if nodes else "TEST_NODE_001"
    await postgres.upsert_node(
        {
            "node_id": test_node,
            "node_name": f"Test Node {test_node}",
            "node_type": "sensor",
            "location_name": "Selargius",
            "is_active": True,
        }
    )
    print(f"✅ Inserted node: {test_node}")

    # Get some recent data for this node
    query = """
    SELECT timestamp, temperature, flow_rate, pressure, volume
    FROM `abbanoa-464816.water_infrastructure.sensor_readings`
    WHERE node_id = '{test_node}'
    AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
    ORDER BY timestamp DESC
    LIMIT 100
    """

    df = client.query(query).to_dataframe()
    print(f"\n📊 Found {len(df)} recent readings for node {test_node}")

    if not df.empty:
        # Convert to sensor readings
        readings = []
        for _, row in df.iterrows():
            readings.append(
                {
                    "timestamp": row["timestamp"].to_pydatetime(),
                    "node_id": test_node,
                    "temperature": (
                        float(row["temperature"]) if row["temperature"] else None
                    ),
                    "flow_rate": float(row["flow_rate"]) if row["flow_rate"] else None,
                    "pressure": float(row["pressure"]) if row["pressure"] else None,
                    "total_flow": float(row["volume"]) if row["volume"] else None,
                    "quality_score": 1.0,
                }
            )

        # Insert batch
        count = await postgres.insert_sensor_readings_batch(readings)
        print(f"✅ Inserted {count} sensor readings")

        # Test Redis cache
        print("\n🔄 Testing Redis cache...")
        from src.infrastructure.cache.redis_cache_manager import RedisCacheManager

        redis_manager = RedisCacheManager()

        # Store latest reading in Redis
        latest = readings[0]
        redis_manager.redis_client.hset(
            f"node:{test_node}:latest",
            mapping={
                "timestamp": latest["timestamp"].isoformat(),
                "flow_rate": str(latest["flow_rate"] or 0),
                "pressure": str(latest["pressure"] or 0),
                "temperature": str(latest["temperature"] or 0),
            },
        )
        print("✅ Cached latest reading in Redis")

        # Verify
        cached = redis_manager.redis_client.hgetall(f"node:{test_node}:latest")
        print(f"📍 Cached data: {cached}")

        print("\n✅ Test data load completed successfully!")
        print("\nYou can now:")
        print(
            "1. Run comprehensive tests: poetry run python test_hybrid_architecture.py"
        )
        print("2. Check the dashboard at http://localhost:8501")
        print(
            "3. Run full ETL: poetry run python -m src.infrastructure.etl.bigquery_to_postgres_etl"
        )
    else:
        print(f"\n⚠️  No recent data found for node {test_node}")


if __name__ == "__main__":
    asyncio.run(test_data_load())

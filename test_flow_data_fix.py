#!/usr/bin/env python3
"""Test script to verify flow data is accessible from BigQuery."""

from google.cloud import bigquery
from datetime import datetime, timedelta

# Initialize client with EU location
client = bigquery.Client(project="abbanoa-464816", location="EU")

print("Testing BigQuery data access...")
print("-" * 50)

# Test 1: Check sensor_readings_ml table
try:
    query = """
    SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT node_id) as unique_nodes,
        MIN(timestamp) as first_reading,
        MAX(timestamp) as last_reading
    FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
    """

    result = list(client.query(query).result())
    if result:
        row = result[0]
        print("✅ sensor_readings_ml table:")
        print(f"   - Total records: {row.total_records:,}")
        print(f"   - Unique nodes: {row.unique_nodes}")
        print(f"   - Date range: {row.first_reading} to {row.last_reading}")
except Exception as e:
    print(f"❌ Error accessing sensor_readings_ml: {e}")

print()

# Test 2: Check flow data for recent period
try:
    # Use March 2025 data (which we know exists)
    query = """
    SELECT 
        node_id,
        COUNT(*) as readings,
        AVG(flow_rate) as avg_flow,
        AVG(pressure) as avg_pressure
    FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
    WHERE timestamp BETWEEN '2025-03-01' AND '2025-03-31'
        AND flow_rate IS NOT NULL
    GROUP BY node_id
    ORDER BY node_id
    """

    print("✅ March 2025 flow data by node:")
    for row in client.query(query).result():
        print(
            f"   - Node {row.node_id}: {row.readings} readings, avg flow: {row.avg_flow:.2f} L/s, avg pressure: {row.avg_pressure:.2f} bar"
        )
except Exception as e:
    print(f"❌ Error fetching flow data: {e}")

print()

# Test 3: Check v_sensor_readings_normalized view
try:
    query = """
    SELECT COUNT(*) as total_records
    FROM `abbanoa-464816.water_infrastructure.v_sensor_readings_normalized`
    """

    result = list(client.query(query).result())
    if result:
        print(
            f"✅ v_sensor_readings_normalized view: {result[0].total_records:,} records"
        )
except Exception as e:
    print(f"❌ Error accessing normalized view: {e}")

print()
print("Test complete!")
print("\nIf all tests passed, the dashboard should now display flow data correctly.")

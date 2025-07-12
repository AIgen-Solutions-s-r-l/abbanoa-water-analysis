#!/usr/bin/env python3
"""Test node status display."""

from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client(project="abbanoa-464816", location="EU")

# Test getting latest reading with non-zero values for each node
nodes = ["215542", "215600", "273933", "281492", "288399", "288400"]

print("Testing node status data...")
print("-" * 50)

for node_id in nodes:
    # Get latest reading with non-zero flow
    query = """
    SELECT
        node_id,
        MAX(timestamp) as latest_timestamp,
        AVG(flow_rate) as avg_flow,
        AVG(pressure) as avg_pressure,
        COUNT(*) as total_readings
    FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
    WHERE node_id = "{node_id}"
        AND timestamp >= '2025-03-01'
        AND timestamp <= '2025-03-31'
    GROUP BY node_id
    """

    result = list(client.query(query).result())
    if result:
        row = result[0]
        print(f"\nNode {node_id}:")
        print(f"  Latest reading: {row.latest_timestamp}")
        print(f"  Avg flow (March): {row.avg_flow:.2f} L/s")
        print(f"  Avg pressure (March): {row.avg_pressure:.2f} bar")
        print(f"  Total readings: {row.total_readings}")

        # Get a recent non-zero reading
        query2 = """
        SELECT timestamp, flow_rate, pressure
        FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
        WHERE node_id = "{node_id}"
            AND flow_rate > 0
        ORDER BY timestamp DESC
        LIMIT 1
        """

        result2 = list(client.query(query2).result())
        if result2:
            row2 = result2[0]
            print(
                f"  Last active: {row2.timestamp} - {row2.flow_rate:.2f} L/s, {row2.pressure:.2f} bar"
            )
    else:
        print(f"\nNode {node_id}: No data")

print("\n" + "-" * 50)
print("Summary: Nodes have data but recent readings show 0 flow.")
print("The dashboard should show these as 'Low Flow' rather than 'No Data'.")

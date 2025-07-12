#!/usr/bin/env python3
"""Test anomaly detection on sensor data."""

from google.cloud import bigquery
client = bigquery.Client(project="abbanoa-464816", location="EU")

print("Testing anomaly detection queries...")
print("-" * 60)

# Test 1: Check for flow anomalies
query = """
WITH flow_stats AS (
    SELECT
        node_id,
        timestamp,
        flow_rate,
        AVG(flow_rate) OVER (
            PARTITION BY node_id
            ORDER BY timestamp
            ROWS BETWEEN 48 PRECEDING AND CURRENT ROW
        ) as avg_flow,
        STDDEV(flow_rate) OVER (
            PARTITION BY node_id
            ORDER BY timestamp
            ROWS BETWEEN 48 PRECEDING AND CURRENT ROW
        ) as stddev_flow
    FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
    WHERE timestamp >= '2025-03-01'
        AND timestamp <= '2025-03-31'
        AND node_id IN ('215542', '273933', '288399', '288400')
)
SELECT
    node_id,
    COUNT(*) as anomaly_count,
    MAX(flow_rate) as max_anomaly_flow,
    AVG(flow_rate) as avg_anomaly_flow
FROM flow_stats
WHERE flow_rate > avg_flow + 2 * stddev_flow
    AND flow_rate > 10
GROUP BY node_id
"""

print("Flow anomalies (2-sigma threshold):")
for row in client.query(query).result():
    print(
        f"  Node {row.node_id}: {row.anomaly_count} anomalies, max flow: {row.max_anomaly_flow:.1f} L/s"
    )

print()

# Test 2: Check for pressure anomalies
query2 = """
SELECT
    node_id,
    COUNT(*) as low_pressure_count,
    MIN(pressure) as min_pressure,
    AVG(pressure) as avg_pressure
FROM `abbanoa-464816.water_infrastructure.sensor_readings_ml`
WHERE timestamp >= '2025-03-01'
    AND timestamp <= '2025-03-31'
    AND pressure < 2.0
    AND pressure > 0
GROUP BY node_id
HAVING COUNT(*) > 0
"""

print("Low pressure events (<2.0 bar):")
for row in client.query(query2).result():
    print(
        f"  Node {row.node_id}: {row.low_pressure_count} events, min: {row.min_pressure:.1f} bar"
    )

print()

# Test 3: Test the simple anomaly detector
try:
    import sys

    sys.path.append("/home/alessio/Customers/Abbanoa")
    from src.presentation.streamlit.utils.simple_anomaly_detector import (
        SimpleAnomalyDetector,
    )

    detector = SimpleAnomalyDetector(client)
    anomalies = detector.detect_anomalies(24 * 30)  # Last 30 days

    print(f"Simple anomaly detector found: {len(anomalies)} anomalies")

    # Show first 5
    for i, anomaly in enumerate(anomalies[:5]):
        print(f"\n{i+1}. {anomaly['node_name']} - {anomaly['timestamp']}")
        print(f"   Type: {anomaly['anomaly_type']}, Severity: {anomaly['severity']}")
        print(f"   {anomaly['description']}")

except Exception as e:
    print(f"Error testing simple anomaly detector: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "-" * 60)
print("If anomalies were found, the dashboard should display them.")

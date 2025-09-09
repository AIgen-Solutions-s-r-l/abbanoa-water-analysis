#!/usr/bin/env python3
"""Populate database with test sensor data and anomalies."""

import asyncio
import asyncpg
import random
from datetime import datetime, timedelta, timezone
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.anomaly_detector import AnomalyDetector


async def main():
    """Generate test data with anomalies."""
    
    # Database connection
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        database='abbanoa_processing',
        user='abbanoa_user',
        password='abbanoa_secure_pass'
    )
    
    print("Connected to database")
    
    # Get some nodes
    nodes_query = "SELECT node_id, node_name FROM water_infrastructure.nodes LIMIT 5"
    nodes = await conn.fetch(nodes_query)
    
    if not nodes:
        print("No nodes found. Creating test nodes...")
        # Create test nodes
        test_nodes = [
            ('NODE-001', 'Central Hub', 'hub', 'active', 44.1385, 12.2486),
            ('NODE-002', 'North Station', 'distribution', 'active', 44.1420, 12.2430),
            ('NODE-003', 'South Zone', 'distribution', 'active', 44.1310, 12.2450),
            ('NODE-004', 'East Network', 'distribution', 'active', 44.1355, 12.2510),
            ('NODE-005', 'West Monitoring', 'monitoring', 'active', 44.1340, 12.2350)
        ]
        
        for node_id, name, node_type, status, lat, lon in test_nodes:
            await conn.execute("""
                INSERT INTO water_infrastructure.nodes 
                (node_id, node_name, node_type, status, latitude, longitude)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (node_id) DO NOTHING
            """, node_id, name, node_type, status, lat, lon)
        
        nodes = await conn.fetch(nodes_query)
    
    print(f"Working with {len(nodes)} nodes")
    
    # Generate sensor readings with some anomalies
    base_time = datetime.now(timezone.utc)
    
    for node in nodes:
        node_id = node['node_id']
        print(f"\nGenerating data for {node_id} - {node['node_name']}")
        
        # Generate 48 hours of data
        for hour in range(48):
            timestamp = base_time - timedelta(hours=hour)
            
            # Normal values
            pressure = 3.0 + random.gauss(0, 0.1)
            flow_rate = 100.0 + random.gauss(0, 5)
            temperature = 15.0 + random.gauss(0, 0.5)
            quality_score = 0.95 + random.gauss(0, 0.02)
            
            # Introduce anomalies for specific hours and nodes
            if node_id == 'NODE-001' and 10 <= hour <= 12:
                # Pressure drop anomaly
                pressure = 1.5 + random.gauss(0, 0.1)
                flow_rate = 150.0 + random.gauss(0, 10)  # Increased flow (leak?)
                print(f"  - Hour {hour}: Pressure drop anomaly (pressure={pressure:.2f}, flow={flow_rate:.2f})")
            
            elif node_id == 'NODE-002' and hour == 20:
                # Quality issue
                quality_score = 0.65
                print(f"  - Hour {hour}: Quality anomaly (quality={quality_score:.2f})")
            
            elif node_id == 'NODE-003' and hour in [5, 6]:
                # Flow spike
                flow_rate = 180.0 + random.gauss(0, 10)
                print(f"  - Hour {hour}: Flow spike anomaly (flow={flow_rate:.2f})")
            
            # Ensure values are within reasonable bounds
            pressure = max(0.5, min(5.0, pressure))
            flow_rate = max(0, min(300, flow_rate))
            temperature = max(5, min(30, temperature))
            quality_score = max(0, min(1.0, quality_score))
            
            # Insert sensor reading
            try:
                await conn.execute("""
                    INSERT INTO water_infrastructure.sensor_readings
                    (timestamp, node_id, pressure, flow_rate, temperature, quality_score)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (timestamp, node_id) DO UPDATE SET
                        pressure = EXCLUDED.pressure,
                        flow_rate = EXCLUDED.flow_rate,
                        temperature = EXCLUDED.temperature,
                        quality_score = EXCLUDED.quality_score
                """, timestamp, node_id, pressure, flow_rate, temperature, quality_score)
            except Exception as e:
                print(f"  Error inserting data: {e}")
    
    print("\n" + "="*50)
    print("Running anomaly detection...")
    print("="*50)
    
    # Run anomaly detection
    detector = AnomalyDetector(conn)
    
    total_anomalies = 0
    for node in nodes:
        node_id = node['node_id']
        print(f"\nDetecting anomalies for {node_id}...")
        
        anomalies = await detector.detect_anomalies(node_id, hours=48)
        
        if anomalies:
            print(f"  Found {len(anomalies)} anomalies:")
            for anomaly in anomalies[:5]:  # Show first 5
                print(f"    - {anomaly['anomaly_type']}: {anomaly['severity']} severity")
                print(f"      {anomaly.get('description', 'No description')}")
            
            total_anomalies += len(anomalies)
        else:
            print("  No anomalies detected")
    
    print(f"\nTotal anomalies detected and saved: {total_anomalies}")
    
    # Verify anomalies were saved
    count_query = "SELECT COUNT(*) FROM water_infrastructure.anomalies WHERE timestamp > NOW() - INTERVAL '48 hours'"
    count = await conn.fetchval(count_query)
    print(f"Anomalies in database: {count}")
    
    # Show some statistics
    stats_query = """
        SELECT 
            anomaly_type, 
            severity, 
            COUNT(*) as count
        FROM water_infrastructure.anomalies
        WHERE timestamp > NOW() - INTERVAL '48 hours'
        GROUP BY anomaly_type, severity
        ORDER BY count DESC
    """
    
    stats = await conn.fetch(stats_query)
    if stats:
        print("\nAnomaly Statistics:")
        for row in stats:
            print(f"  {row['anomaly_type']} ({row['severity']}): {row['count']} occurrences")
    
    await conn.close()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
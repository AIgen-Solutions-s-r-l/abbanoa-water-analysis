#!/usr/bin/env python3
"""Test script to verify the fixed repository is working correctly."""

import asyncio
import sys
import os
import traceback
from datetime import datetime, timedelta
from uuid import UUID

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infrastructure.di_container import Container
from src.infrastructure.repositories.sensor_data_repository import SensorDataRepository
from src.infrastructure.repositories.static_monitoring_node_repository import StaticMonitoringNodeRepository


async def test_fixed_repository():
    """Test the fixed repository implementation."""
    print("🔧 Testing Fixed Repository Implementation...")
    print("=" * 60)
    
    # Initialize container
    container = Container()
    container.config.from_dict({
        "bigquery": {
            "project_id": "abbanoa-464816",
            "dataset_id": "water_infrastructure",
            "credentials_path": None,
            "location": "EU",
        }
    })
    
    # Test 1: Repository initialization
    print("\n1. Testing Repository Initialization...")
    try:
        sensor_repo = container.sensor_reading_repository()
        node_repo = container.monitoring_node_repository()
        print("✅ Repositories initialized successfully")
    except Exception as e:
        print(f"❌ Repository initialization failed: {e}")
        return
    
    # Test 2: Node repository
    print("\n2. Testing Node Repository...")
    try:
        nodes = await node_repo.get_all()
        print(f"✅ Found {len(nodes)} monitoring nodes:")
        for node in nodes:
            print(f"  - {node.name} ({node.id})")
    except Exception as e:
        print(f"❌ Node repository test failed: {e}")
        return
    
    # Test 3: Data fetching for primary node
    print("\n3. Testing Data Fetching for Primary Node...")
    try:
        primary_node_id = UUID("00000000-0000-0000-0000-000000000001")
        
        # Use data range from the diagnostics
        end_time = datetime(2025, 4, 1, 6, 0, 0)
        start_time = end_time - timedelta(days=1)
        
        readings = await sensor_repo.get_by_node_id(
            node_id=primary_node_id,
            start_time=start_time,
            end_time=end_time,
            limit=10
        )
        
        print(f"✅ Retrieved {len(readings)} readings from primary node")
        if readings:
            print("   Sample readings:")
            for i, reading in enumerate(readings[:3]):
                print(f"   [{i+1}] {reading.timestamp}: Flow={reading.flow_rate}, Temp={reading.temperature}, Pressure={reading.pressure}")
                
    except Exception as e:
        print(f"❌ Data fetching test failed: {e}")
        traceback.print_exc()
        return
    
    # Test 4: Data fetching for multiple nodes
    print("\n4. Testing Data Fetching for Multiple Nodes...")
    try:
        node_ids = [
            UUID("00000000-0000-0000-0000-000000000001"),
            UUID("00000000-0000-0000-0000-000000000002"),
            UUID("00000000-0000-0000-0000-000000000003"),
        ]
        
        total_readings = 0
        for node_id in node_ids:
            readings = await sensor_repo.get_by_node_id(
                node_id=node_id,
                start_time=start_time,
                end_time=end_time,
                limit=5
            )
            total_readings += len(readings)
            print(f"   Node {node_id}: {len(readings)} readings")
        
        print(f"✅ Retrieved {total_readings} total readings from multiple nodes")
        
    except Exception as e:
        print(f"❌ Multiple node test failed: {e}")
        traceback.print_exc()
        return
    
    # Test 5: Anomaly detection
    print("\n5. Testing Anomaly Detection...")
    try:
        anomalies = await sensor_repo.get_anomalous_readings(
            start_time=start_time,
            end_time=end_time
        )
        
        print(f"✅ Found {len(anomalies)} anomalous readings")
        if anomalies:
            print("   Sample anomalies:")
            for i, anomaly in enumerate(anomalies[:3]):
                print(f"   [{i+1}] {anomaly.timestamp}: Node={anomaly.node_id}, Flow={anomaly.flow_rate}, Temp={anomaly.temperature}")
                
    except Exception as e:
        print(f"❌ Anomaly detection test failed: {e}")
        traceback.print_exc()
        return
    
    # Test 6: Dashboard integration test
    print("\n6. Testing Dashboard Integration...")
    try:
        from src.application.use_cases.detect_network_anomalies import DetectNetworkAnomaliesUseCase
        
        print("   6.1: Creating use case...")
        anomaly_use_case = container.detect_network_anomalies_use_case()
        
        print("   6.2: Running use case with 24-hour window...")
        # Test with shorter time window
        anomaly_results = await anomaly_use_case.execute(
            time_window_hours=24,
            notify_on_critical=False
        )
        
        print(f"✅ Dashboard integration test passed: {len(anomaly_results)} anomalies detected")
        
    except Exception as e:
        print(f"❌ Dashboard integration test failed: {e}")
        print("Detailed error information:")
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! Repository is working correctly.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_fixed_repository()) 
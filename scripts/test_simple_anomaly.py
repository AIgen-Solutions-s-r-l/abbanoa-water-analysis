#!/usr/bin/env python3
"""Simple test script to isolate the anomaly detection issue."""

import asyncio
import sys
import os
import traceback
from datetime import datetime, timedelta
from uuid import UUID

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infrastructure.di_container import Container


async def test_simple_anomaly():
    """Test anomaly detection step by step."""
    print("🔍 Testing Simple Anomaly Detection...")
    print("=" * 60)
    
    try:
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
        
        print("1. Testing sensor repository...")
        sensor_repo = container.sensor_reading_repository()
        
        # Test with a shorter time window
        end_time = datetime(2025, 4, 1, 6, 0, 0)
        start_time = end_time - timedelta(hours=1)
        
        print("2. Fetching sample readings...")
        node_id = UUID("00000000-0000-0000-0000-000000000003")  # Node that had data
        
        readings = await sensor_repo.get_by_node_id(
            node_id=node_id,
            start_time=start_time,
            end_time=end_time,
            limit=20
        )
        
        print(f"   Retrieved {len(readings)} readings")
        
        if not readings:
            print("❌ No readings found, cannot test anomaly detection")
            return
        
        print("3. Testing anomaly detection service directly...")
        from src.domain.services.anomaly_detection_service import AnomalyDetectionService
        
        anomaly_service = AnomalyDetectionService()
        
        print("4. Running anomaly detection...")
        anomalies = anomaly_service.detect_anomalies(readings)
        
        print(f"✅ Anomaly detection completed: {len(anomalies)} anomalies found")
        
        print("5. Testing use case...")
        use_case = container.detect_network_anomalies_use_case()
        
        print("6. Running use case with short time window...")
        result = await use_case.execute(
            time_window_hours=1,
            notify_on_critical=False
        )
        
        print(f"✅ Use case completed: {len(result)} anomalies detected")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("Full traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple_anomaly()) 
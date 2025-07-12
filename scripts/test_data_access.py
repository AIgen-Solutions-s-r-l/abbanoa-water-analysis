#!/usr/bin/env python3
"""Test data access with proper date handling."""

import asyncio
from datetime import datetime, timedelta
from uuid import UUID
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infrastructure.di_container import Container
from src.infrastructure.persistence.bigquery_config import BigQueryConfig, BigQueryConnection
from src.infrastructure.repositories.sensor_data_repository import SensorDataRepository


async def test_data_access():
    """Test accessing BigQuery data."""
    # Configure connection
    config = BigQueryConfig(
        project_id="abbanoa-464816",
        dataset_id="water_infrastructure",
        location="EU"
    )
    
    connection = BigQueryConnection(config)
    repo = SensorDataRepository(connection)
    
    # Test 1: Get data for a specific node using the latest available date
    print("Test 1: Getting data for Sant'Anna node...")
    node_id = UUID('00000000-0000-0000-0000-000000000001')  # Sant'Anna
    
    # Use a date range that includes the future dates in the data
    end_date = datetime(2025, 3, 31, 23, 59, 59)  # Latest date in data
    start_date = end_date - timedelta(days=7)
    
    readings = await repo.get_by_node_id(
        node_id=node_id,
        start_time=start_date,
        end_time=end_date,
        limit=10
    )
    
    print(f"Found {len(readings)} readings")
    if readings:
        print("\nSample readings:")
        for reading in readings[:5]:
            print(f"  {reading.timestamp}: Flow={reading.flow_rate.value if reading.flow_rate else 'N/A'} L/s, "
                  f"Temp={reading.temperature.value if reading.temperature else 'N/A'}°C, "
                  f"Pressure={reading.pressure.value if reading.pressure else 'N/A'} bar")
    
    # Test 2: Get anomalous readings
    print("\n\nTest 2: Getting anomalous readings...")
    anomalous = await repo.get_anomalous_readings(
        start_time=start_date,
        end_time=end_date
    )
    
    print(f"Found {len(anomalous)} anomalous readings")
    if anomalous:
        print("\nSample anomalous readings:")
        for reading in anomalous[:5]:
            print(f"  {reading.timestamp}: Flow={reading.flow_rate.value if reading.flow_rate else 'N/A'} L/s")
    
    # Test 3: Get all nodes data
    print("\n\nTest 3: Getting data for all nodes...")
    all_node_ids = [
        UUID('00000000-0000-0000-0000-000000000001'),  # Sant'Anna
        UUID('00000000-0000-0000-0000-000000000002'),  # Seneca
        UUID('00000000-0000-0000-0000-000000000003'),  # Serbatoio
    ]
    
    for node_id in all_node_ids:
        latest = await repo.get_latest_by_node(node_id)
        if latest:
            print(f"  Node {node_id}: Latest reading at {latest.timestamp}")


async def test_use_case():
    """Test the consumption analysis use case."""
    print("\n\nTest 4: Testing consumption analysis use case...")
    
    # Initialize container
    container = Container()
    container.config.bigquery.project_id.from_value("abbanoa-464816")
    container.config.bigquery.dataset_id.from_value("water_infrastructure")
    container.config.bigquery.location.from_value("EU")
    container.config.bigquery.credentials_path.from_value(None)
    
    # Get use case
    use_case = container.analyze_consumption_patterns_use_case()
    
    # Use future dates that match our data
    end_date = datetime(2025, 3, 31, 23, 59, 59)
    start_date = end_date - timedelta(days=7)
    node_id = UUID('00000000-0000-0000-0000-000000000001')
    
    try:
        result = await use_case.execute(
            node_id=node_id,
            start_date=start_date,
            end_date=end_date,
            pattern_type="daily"
        )
        
        print("✅ Consumption analysis successful!")
        print("  Average consumption by day:")
        for day, consumption in result.average_consumption.items():
            print(f"    {day}: {consumption} L/s")
        print(f"  Peak hours: {result.peak_hours}")
        print(f"  Off-peak hours: {result.off_peak_hours}")
        print(f"  Variability: {result.variability_coefficient}%")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Main entry point."""
    print("Testing BigQuery data access with proper date handling...\n")
    
    # Run async tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Test repository
    loop.run_until_complete(test_data_access())
    
    # Test use case
    loop.run_until_complete(test_use_case())
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()
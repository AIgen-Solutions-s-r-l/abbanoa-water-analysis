"""
Simple test for ConsumptionService to verify real data access.
"""

import pytest
from datetime import datetime
from src.infrastructure.database.consumption_service import ConsumptionService


def test_consumption_service_connection():
    """Test that ConsumptionService can connect to the database."""
    # Arrange
    database_url = "postgresql://abbanoa_user:abbanoa_secure_pass@localhost:5432/abbanoa_processing"
    
    # Act & Assert
    try:
        service = ConsumptionService(database_url)
        session = service.get_session()
        
        # Try to get a simple count to verify connection works
        from src.infrastructure.database.models import SensorReading
        count = session.query(SensorReading).count()
        
        print(f"Successfully connected to database. Found {count} sensor readings.")
        assert count > 0, "Should have sensor readings in the database"
        
        session.close()
        
    except Exception as e:
        pytest.fail(f"Failed to connect to database: {e}")


def test_consumption_service_real_data():
    """Test that ConsumptionService returns real data."""
    # Arrange
    database_url = "postgresql://abbanoa_user:abbanoa_secure_pass@localhost:5432/abbanoa_processing"
    service = ConsumptionService(database_url)
    
    # Act
    result = service.get_consumption_analytics()
    
    # Assert
    assert 'data_metadata' in result
    metadata = result['data_metadata']
    
    print(f"Data metadata: {metadata}")
    
    # Verify we have real data
    assert metadata['total_readings'] > 0
    assert metadata['active_nodes'] > 0
    assert metadata['is_real_time'] is False
    assert metadata['data_source'] == 'Historical Database'
    
    # Verify date range
    earliest = datetime.fromisoformat(metadata['earliest_timestamp'].replace('Z', '+00:00'))
    latest = datetime.fromisoformat(metadata['latest_timestamp'].replace('Z', '+00:00'))
    
    print(f"Date range: {earliest} to {latest}")
    
    assert earliest.year == 2024
    assert latest.year == 2025
    assert earliest < latest

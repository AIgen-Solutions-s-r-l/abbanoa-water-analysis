"""Integration tests for pressure zones endpoint."""

import os
import httpx
import pytest
from unittest.mock import patch, AsyncMock


API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


@patch('src.presentation.api.endpoints.pressure_router.get_db_connection')
def test_pressure_zones_returns_proper_structure(mock_get_db_connection):
    """Test that pressure zones endpoint returns proper structure."""
    # Arrange
    mock_conn = AsyncMock()
    mock_get_db_connection.return_value = mock_conn
    
    # Mock pressure zones query response
    mock_conn.fetch.return_value = [
        {
            'zone_id': 'ZONE_A',
            'zone_name': 'Test Zone A',
            'min_pressure': 2.5,
            'avg_pressure': 3.2,
            'max_pressure': 3.8,
            'node_count': 5
        },
        {
            'zone_id': 'ZONE_B', 
            'zone_name': 'Test Zone B',
            'min_pressure': 2.8,
            'avg_pressure': 3.5,
            'max_pressure': 4.1,
            'node_count': 3
        }
    ]
    
    url = f"{API_BASE}/pressure/zones"
    resp = httpx.get(url, timeout=10)
    
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    data = resp.json()
    assert "zones" in data, "Response must contain 'zones' key"
    assert isinstance(data["zones"], list), "zones must be a list"
    
    # Validate zone structure
    if data["zones"]:
        zone = data["zones"][0]
        required_fields = [
            "zone",
            "zoneName", 
            "minPressure",
            "avgPressure",
            "maxPressure",
            "nodeCount",
            "status"
        ]
        for field in required_fields:
            assert field in zone, f"Zone missing required field: {field}"
        
        # Validate field types
        assert isinstance(zone["zone"], str)
        assert isinstance(zone["zoneName"], str)
        assert isinstance(zone["minPressure"], (int, float))
        assert isinstance(zone["avgPressure"], (int, float))
        assert isinstance(zone["maxPressure"], (int, float))
        assert isinstance(zone["nodeCount"], int)
        assert isinstance(zone["status"], str)
        
        # Validate logical constraints
        assert zone["minPressure"] <= zone["maxPressure"]
        assert zone["nodeCount"] >= 0
        assert zone["status"] in ["normal", "warning", "critical"]
    
    # Verify mock was called
    mock_get_db_connection.assert_called()



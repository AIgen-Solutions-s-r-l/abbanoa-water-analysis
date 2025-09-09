"""Integration tests for the infrastructure API endpoint."""

import asyncio
from datetime import datetime
import os
import pytest
from unittest.mock import patch, AsyncMock


@patch('src.presentation.api.endpoints.infrastructure_router.get_db_connection')
async def test_infrastructure_map_data(mock_get_db_connection):
    """Test the infrastructure map data endpoint."""
    from src.presentation.api.endpoints.infrastructure_router import get_infrastructure_map_data
    
    # Arrange
    mock_conn = AsyncMock()
    mock_get_db_connection.return_value = mock_conn
    
    # Mock nodes data query
    mock_conn.fetch.side_effect = [
        # First call: nodes query
        [
            {
                'node_id': 'TEST_NODE_1',
                'node_name': 'Test Node 1',
                'node_type': 'distribution',
                'latitude': 40.9179,
                'longitude': 9.4944,
                'is_active': True,
                'flow_rate': 15.2,
                'pressure': 3.1,
                'last_reading': datetime.now(),
                'has_anomaly': False
            }
        ],
        # Second call: zones query (may fail)
        []
    ]
    
    # Mock alert count query
    mock_conn.fetchrow.return_value = {'alert_count': 2}
    
    # Act
    result = await get_infrastructure_map_data()
    
    # Assert
    assert "network_health" in result
    assert "total_flow" in result
    assert "avg_pressure" in result
    assert "active_alerts" in result
    assert "nodes" in result
    assert "zones" in result
    assert "last_updated" in result
    
    # Check data types
    assert isinstance(result["network_health"], (int, float))
    assert isinstance(result["total_flow"], (int, float))
    assert isinstance(result["avg_pressure"], (int, float))
    assert isinstance(result["active_alerts"], int)
    assert isinstance(result["nodes"], list)
    assert isinstance(result["zones"], list)
    
    # Check node structure
    if result["nodes"]:
        node = result["nodes"][0]
        assert "id" in node
        assert "name" in node
        assert "latitude" in node
        assert "longitude" in node
        assert "type" in node
        assert "status" in node
        assert "flow_rate" in node
        assert "pressure" in node
        assert "has_anomaly" in node
    
    # Verify mock was called
    mock_get_db_connection.assert_called()


@patch('src.presentation.api.endpoints.infrastructure_router.get_db_connection')
async def test_network_summary(mock_get_db_connection):
    """Test the network summary endpoint."""
    from src.presentation.api.endpoints.infrastructure_router import get_network_summary
    
    # Arrange
    mock_conn = AsyncMock()
    mock_get_db_connection.return_value = mock_conn
    
    # Mock network stats query
    mock_conn.fetchrow.side_effect = [
        # First call: network stats
        {
            'total_nodes': 10,
            'active_nodes': 8,
            'nodes_with_readings': 6,
            'avg_flow_rate': 12.5,
            'avg_pressure': 3.2,
            'oldest_reading': datetime.now(),
            'latest_reading': datetime.now()
        },
        # Second call: anomaly stats
        {
            'total_anomalies': 3,
            'active_anomalies': 1,
            'critical_anomalies': 0
        }
    ]
    
    # Act
    result = await get_network_summary()
    
    # Assert
    assert "network" in result
    assert "anomalies" in result
    assert "timestamp" in result
    
    # Check network structure
    network = result["network"]
    assert "total_nodes" in network
    assert "active_nodes" in network
    assert "nodes_with_readings" in network
    assert "avg_flow_rate" in network
    assert "avg_pressure" in network
    assert "data_range" in network
    
    # Check data types
    assert isinstance(network["total_nodes"], int)
    assert isinstance(network["active_nodes"], int)
    assert isinstance(network["nodes_with_readings"], int)
    assert isinstance(network["avg_flow_rate"], (int, float))
    assert isinstance(network["avg_pressure"], (int, float))
    
    # Check anomalies structure
    anomalies = result["anomalies"]
    assert "total_24h" in anomalies
    assert "active" in anomalies
    assert "critical" in anomalies
    
    # Check data types
    assert isinstance(anomalies["total_24h"], int)
    assert isinstance(anomalies["active"], int)
    assert isinstance(anomalies["critical"], int)
    
    # Verify mock was called
    mock_get_db_connection.assert_called()


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_infrastructure_map_data())
    asyncio.run(test_network_summary())
    print("✅ All infrastructure endpoint tests passed!")
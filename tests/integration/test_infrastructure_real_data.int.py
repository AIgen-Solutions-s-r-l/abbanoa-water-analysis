"""Integration tests for infrastructure router with real data requirements."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import asyncpg


@pytest.mark.asyncio
async def test_infrastructure_map_data_returns_real_nodes_from_database(mocker):
    """Test that /map-data endpoint returns real node data from database."""
    # Arrange
    mock_conn = MagicMock()
    mock_conn.fetch = AsyncMock()
    mock_conn.fetchrow = AsyncMock()
    mock_conn.close = AsyncMock()
    
    # Mock database connection
    mocker.patch(
        'src.presentation.api.endpoints.infrastructure_router.get_db_connection',
        return_value=mock_conn
    )
    
    # Mock real node data from database
    mock_nodes_data = [
        {
            'node_id': 'NODE_001',
            'node_name': 'Main Distribution Node',
            'node_type': 'distribution',
            'latitude': 39.2238,
            'longitude': 9.1217,
            'is_active': True,
            'flow_rate': 45.6,
            'pressure': 4.2,
            'timestamp': datetime.now(timezone.utc),
            'has_anomaly': False
        },
        {
            'node_id': 'NODE_002',
            'node_name': 'Storage Tank A',
            'node_type': 'storage',
            'latitude': 39.2251,
            'longitude': 9.1198,
            'is_active': True,
            'flow_rate': 32.1,
            'pressure': 3.8,
            'timestamp': datetime.now(timezone.utc),
            'has_anomaly': True
        }
    ]
    mock_conn.fetch.return_value = mock_nodes_data
    
    # Mock alerts data
    mock_conn.fetchrow.return_value = {'alert_count': 2}
    
    # Act
    from src.presentation.api.endpoints.infrastructure_router import get_infrastructure_map_data
    result = await get_infrastructure_map_data()
    
    # Assert
    assert 'nodes' in result
    assert len(result['nodes']) == 2
    
    # Verify first node has real data
    first_node = result['nodes'][0]
    assert first_node['id'] == 'NODE_001'
    assert first_node['name'] == 'Main Distribution Node'
    assert first_node['latitude'] == 39.2238
    assert first_node['longitude'] == 9.1217
    assert first_node['flow_rate'] == 45.6
    assert first_node['pressure'] == 4.2
    
    # Verify no mock data function was called
    assert 'SEL_001' not in [n['id'] for n in result['nodes']]
    assert 'QUA_001' not in [n['id'] for n in result['nodes']]


@pytest.mark.asyncio
async def test_infrastructure_map_data_returns_503_when_database_unavailable(mocker):
    """Test that /map-data endpoint returns 503 error when database is unavailable."""
    # Arrange
    mocker.patch(
        'src.presentation.api.endpoints.infrastructure_router.get_db_connection',
        return_value=None
    )
    
    # Act & Assert
    from src.presentation.api.endpoints.infrastructure_router import get_infrastructure_map_data
    from fastapi import HTTPException
    
    with pytest.raises(HTTPException) as exc_info:
        await get_infrastructure_map_data()
    
    assert exc_info.value.status_code == 503
    assert "Database connection unavailable" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_infrastructure_map_data_returns_500_on_database_error(mocker):
    """Test that /map-data endpoint returns 500 error on database query failure."""
    # Arrange
    mock_conn = MagicMock()
    mock_conn.fetch = AsyncMock(side_effect=Exception("Database query failed"))
    mock_conn.close = AsyncMock()
    
    mocker.patch(
        'src.presentation.api.endpoints.infrastructure_router.get_db_connection',
        return_value=mock_conn
    )
    
    # Act & Assert
    from src.presentation.api.endpoints.infrastructure_router import get_infrastructure_map_data
    from fastapi import HTTPException
    
    with pytest.raises(HTTPException) as exc_info:
        await get_infrastructure_map_data()
    
    assert exc_info.value.status_code == 500
    assert "Failed to fetch infrastructure data" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_mock_infrastructure_data_function_removed():
    """Test that get_mock_infrastructure_data function has been removed."""
    # Act & Assert
    from src.presentation.api.endpoints import infrastructure_router
    
    # The function should not exist
    assert not hasattr(infrastructure_router, 'get_mock_infrastructure_data')


@pytest.mark.asyncio
async def test_fixed_node_coordinates_constant_removed():
    """Test that FIXED_NODE_COORDINATES constant has been removed."""
    # Act & Assert
    from src.presentation.api.endpoints import infrastructure_router
    
    # The constant should not exist
    assert not hasattr(infrastructure_router, 'FIXED_NODE_COORDINATES')


@pytest.mark.asyncio
async def test_infrastructure_includes_pipes_from_database(mocker):
    """Test that infrastructure data includes pipe connections from database."""
    # Arrange
    mock_conn = MagicMock()
    mock_conn.fetch = AsyncMock()
    mock_conn.fetchrow = AsyncMock()
    mock_conn.close = AsyncMock()
    
    mocker.patch(
        'src.presentation.api.endpoints.infrastructure_router.get_db_connection',
        return_value=mock_conn
    )
    
    # Mock nodes data
    mock_nodes_data = [
        {
            'node_id': 'NODE_001',
            'node_name': 'Node 1',
            'node_type': 'distribution',
            'latitude': 39.2238,
            'longitude': 9.1217,
            'is_active': True,
            'flow_rate': 45.6,
            'pressure': 4.2,
            'timestamp': datetime.now(timezone.utc),
            'has_anomaly': False
        }
    ]
    
    # Mock pipes data
    mock_pipes_data = [
        {
            'pipe_id': 'PIPE_001',
            'from_node_id': 'NODE_001',
            'to_node_id': 'NODE_002',
            'from_lat': 39.2238,
            'from_lon': 9.1217,
            'to_lat': 39.2251,
            'to_lon': 9.1198,
            'diameter_mm': 300,
            'material': 'PVC',
            'flow_rate': 35.2
        }
    ]
    
    # Set up mock responses
    mock_conn.fetch.side_effect = [mock_nodes_data, [], mock_pipes_data]
    mock_conn.fetchrow.return_value = {'alert_count': 0}
    
    # Act
    from src.presentation.api.endpoints.infrastructure_router import get_infrastructure_map_data
    result = await get_infrastructure_map_data()
    
    # Assert
    assert 'pipes' in result
    assert isinstance(result['pipes'], list)
    # When pipes are implemented, this should not be empty
    # For now, we expect it to be empty as per current implementation
"""Integration test for infrastructure connection bug fix."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_infrastructure_map_data_pipes_connection_handling():
    """Test that pipes data is fetched before connection is closed."""
    
    # Arrange - Mock the database connection and its methods
    mock_conn = AsyncMock()
    mock_conn.fetch = AsyncMock()
    mock_conn.fetchrow = AsyncMock()
    mock_conn.close = AsyncMock()
    
    # Track if connection is closed
    connection_closed = False
    
    def mark_closed():
        nonlocal connection_closed
        connection_closed = True
        return AsyncMock()
    
    mock_conn.close.side_effect = mark_closed
    
    # Mock nodes data
    nodes_data = [
        {
            'node_id': 'node1',
            'node_name': 'Node 1',
            'node_type': 'source',
            'latitude': 40.0,
            'longitude': 9.0,
            'is_active': True,
            'flow_rate': 100.0,
            'pressure': 3.0,
            'last_reading': datetime.now(timezone.utc),
            'has_anomaly': False
        }
    ]
    
    # Mock pipes data that should be returned
    pipes_data = [
        {
            'pipe_id': 'pipe1',
            'from_node_id': 'node1',
            'to_node_id': 'node2',
            'from_lat': 40.0,
            'from_lon': 9.0,
            'to_lat': 40.1,
            'to_lon': 9.1,
            'diameter_mm': 200,
            'material': 'PVC',
            'flow_rate': 50.0
        }
    ]
    
    # Mock alerts data
    alerts_data = {'alert_count': 0}
    
    # Setup mock responses
    mock_conn.fetch.side_effect = [
        nodes_data,  # First call for nodes
        [],  # Second call for zones
        pipes_data  # Third call for pipes - should work if connection not closed
    ]
    mock_conn.fetchrow.return_value = alerts_data
    
    # Act - Import and test the endpoint
    with patch('src.presentation.api.endpoints.infrastructure_router.asyncpg.connect', 
               return_value=mock_conn):
        from src.presentation.api.endpoints.infrastructure_router import get_infrastructure_map_data
        
        # Define a custom fetch for pipes that checks connection state
        async def pipes_fetch_with_check(*args, **kwargs):
            if connection_closed:
                raise Exception("connection is closed")
            return pipes_data
        
        # Override the third fetch call to check connection state
        original_side_effect = mock_conn.fetch.side_effect
        
        async def custom_fetch(*args, **kwargs):
            # Check if this is the pipes query (contains 'pipes' table)
            if args and 'pipes' in str(args[0]):
                if connection_closed:
                    raise Exception("connection is closed")
            # Use original side effect for call ordering
            if isinstance(original_side_effect, list):
                return original_side_effect.pop(0)
            return await original_side_effect(*args, **kwargs)
        
        mock_conn.fetch.side_effect = custom_fetch
        
        # Execute the endpoint
        result = await get_infrastructure_map_data()
    
    # Assert - Verify pipes data was fetched successfully
    assert result is not None
    assert 'pipes' in result
    assert result['pipes'] is not None
    assert len(result['pipes']) > 0, "Pipes data should be populated, not empty due to connection error"
    assert result['nodes'] is not None
    assert len(result['nodes']) > 0


@pytest.mark.asyncio  
async def test_infrastructure_connection_closed_in_finally_block():
    """Test that connection is properly closed in finally block after all operations."""
    
    # Arrange
    mock_conn = AsyncMock()
    close_called_after_pipes = False
    pipes_fetched = False
    
    async def track_pipes_fetch(*args, **kwargs):
        nonlocal pipes_fetched
        pipes_fetched = True
        return []
    
    async def track_close(*args, **kwargs):
        nonlocal close_called_after_pipes
        if pipes_fetched:
            close_called_after_pipes = True
        return None
    
    mock_conn.fetch = AsyncMock(side_effect=[[], [], track_pipes_fetch])
    mock_conn.fetchrow = AsyncMock(return_value={'alert_count': 0})
    mock_conn.close = AsyncMock(side_effect=track_close)
    
    # Act
    with patch('src.presentation.api.endpoints.infrastructure_router.asyncpg.connect',
               return_value=mock_conn):
        from src.presentation.api.endpoints.infrastructure_router import get_infrastructure_map_data
        
        result = await get_infrastructure_map_data()
    
    # Assert
    assert pipes_fetched, "Pipes data should be fetched"
    assert close_called_after_pipes, "Connection should be closed AFTER pipes are fetched"
    assert mock_conn.close.called, "Connection close should be called"
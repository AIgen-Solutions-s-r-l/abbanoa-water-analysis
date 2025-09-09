"""Integration tests for nodes endpoint."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone


@pytest.fixture
def mock_db_connection(mocker):
    """Mock database connection."""
    mock_conn = AsyncMock()
    mock_connect = mocker.patch(
        'src.presentation.api.endpoints.nodes_router.asyncpg.connect',
        return_value=mock_conn
    )
    return mock_conn


@pytest.fixture
def sample_nodes_data():
    """Generate sample nodes data for testing."""
    return [
        {
            'node_id': 'NODE-001',
            'node_name': 'Central Station A',
            'node_type': 'pump_station',
            'location_lat': 39.2163,
            'location_lng': 9.1064,
            'status': 'active',
            'last_reading': datetime.now(timezone.utc),
            'capacity': 1000.0,
            'current_flow': 850.0
        },
        {
            'node_id': 'NODE-002', 
            'node_name': 'Distribution Point B',
            'node_type': 'distribution',
            'location_lat': 39.2200,
            'location_lng': 9.1100,
            'status': 'active',
            'last_reading': datetime.now(timezone.utc),
            'capacity': 500.0,
            'current_flow': 420.0
        },
        {
            'node_id': 'NODE-003',
            'node_name': 'Reservoir C',
            'node_type': 'reservoir',
            'location_lat': 39.2100,
            'location_lng': 9.1000,
            'status': 'maintenance',
            'last_reading': datetime.now(timezone.utc),
            'capacity': 2000.0,
            'current_flow': 0.0
        }
    ]


class TestNodesEndpoint:
    """Test nodes endpoint functionality."""
    
    def test_get_nodes_returns_list_of_nodes(self, mock_db_connection, sample_nodes_data):
        """Should return a list of network nodes with their details."""
        # Arrange
        mock_db_connection.fetch.return_value = sample_nodes_data
        mock_db_connection.close = AsyncMock()
        
        from src.presentation.api.app_postgres import app
        client = TestClient(app)
        
        # Act
        response = client.get("/api/v1/nodes")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert len(data["nodes"]) == 3
        
        # Verify node structure
        node = data["nodes"][0]
        assert "node_id" in node
        assert "node_name" in node
        assert "node_type" in node
        assert "location" in node
        assert "status" in node
        assert "capacity" in node
        assert "current_flow" in node
        assert "last_reading" in node
    
    def test_get_nodes_with_status_filter(self, mock_db_connection, sample_nodes_data):
        """Should filter nodes by status when status parameter provided."""
        # Arrange
        active_nodes = [n for n in sample_nodes_data if n['status'] == 'active']
        mock_db_connection.fetch.return_value = active_nodes
        mock_db_connection.close = AsyncMock()
        
        from src.presentation.api.app_postgres import app
        client = TestClient(app)
        
        # Act
        response = client.get("/api/v1/nodes?status=active")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 2
        for node in data["nodes"]:
            assert node["status"] == "active"
    
    def test_get_nodes_with_node_type_filter(self, mock_db_connection, sample_nodes_data):
        """Should filter nodes by type when node_type parameter provided."""
        # Arrange
        pump_stations = [n for n in sample_nodes_data if n['node_type'] == 'pump_station']
        mock_db_connection.fetch.return_value = pump_stations
        mock_db_connection.close = AsyncMock()
        
        from src.presentation.api.app_postgres import app
        client = TestClient(app)
        
        # Act
        response = client.get("/api/v1/nodes?node_type=pump_station")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["node_type"] == "pump_station"
    
    def test_get_nodes_empty_database(self, mock_db_connection):
        """Should return empty list when no nodes in database."""
        # Arrange
        mock_db_connection.fetch.return_value = []
        mock_db_connection.close = AsyncMock()
        
        from src.presentation.api.app_postgres import app
        client = TestClient(app)
        
        # Act
        response = client.get("/api/v1/nodes")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["nodes"] == []
        assert data["total_nodes"] == 0
    
    def test_get_nodes_database_error(self, mock_db_connection):
        """Should return 500 error when database connection fails."""
        # Arrange
        mock_db_connection.fetch.side_effect = Exception("Database connection failed")
        
        from src.presentation.api.app_postgres import app
        client = TestClient(app)
        
        # Act
        response = client.get("/api/v1/nodes")
        
        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
    
    def test_get_nodes_returns_summary_statistics(self, mock_db_connection, sample_nodes_data):
        """Should return summary statistics along with nodes data."""
        # Arrange
        mock_db_connection.fetch.return_value = sample_nodes_data
        mock_db_connection.close = AsyncMock()
        
        from src.presentation.api.app_postgres import app
        client = TestClient(app)
        
        # Act
        response = client.get("/api/v1/nodes")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert data["summary"]["total_nodes"] == 3
        assert data["summary"]["active_nodes"] == 2
        assert data["summary"]["maintenance_nodes"] == 1
        assert data["summary"]["total_capacity"] == 3500.0
        assert data["summary"]["total_current_flow"] == 1270.0
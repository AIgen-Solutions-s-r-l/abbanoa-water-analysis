"""Integration tests for anomalies endpoint - real data only behavior."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from fastapi.testclient import TestClient


@pytest.fixture
def mock_db_connection(mocker):
    """Mock database connection for testing."""
    mock_conn = AsyncMock()
    mock_connect = mocker.patch(
        'src.presentation.api.endpoints.anomaly_router.asyncpg.connect',
        return_value=mock_conn
    )
    return mock_conn


@pytest.fixture
def client():
    """Create test client."""
    from src.presentation.api.app_postgres import app
    return TestClient(app)


class TestAnomaliesRealDataOnly:
    """Test that anomalies endpoint returns only real data, no mocks."""
    
    async def test_returns_empty_list_when_no_anomalies(self, client, mock_db_connection):
        """Should return empty list when database has no anomalies."""
        # Arrange
        mock_db_connection.fetch.return_value = []
        mock_db_connection.close = AsyncMock()
        
        # Act
        response = client.get("/api/v1/anomalies")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []
        mock_db_connection.fetch.assert_called_once()
        mock_db_connection.close.assert_called_once()
    
    async def test_returns_real_anomalies_from_database(self, client, mock_db_connection):
        """Should return only real anomalies from database."""
        # Arrange
        real_anomalies = [
            {
                'id': 1,
                'node_id': 'NODE-001',
                'node_name': 'Central Hub',
                'timestamp': datetime.now(timezone.utc),
                'anomaly_type': 'pressure_drop',
                'severity': 'high',
                'measurement_type': 'pressure',
                'actual_value': 1.5,
                'expected_value': 3.0,
                'deviation_percentage': 50.0,
                'description': 'Pressure drop detected',
                'resolved_at': None
            },
            {
                'id': 2,
                'node_id': 'NODE-002',
                'node_name': 'North Station',
                'timestamp': datetime.now(timezone.utc),
                'anomaly_type': 'flow_anomaly',
                'severity': 'medium',
                'measurement_type': 'flow',
                'actual_value': 120.5,
                'expected_value': 100.0,
                'deviation_percentage': 20.5,
                'description': 'Flow anomaly detected',
                'resolved_at': None
            }
        ]
        mock_db_connection.fetch.return_value = real_anomalies
        mock_db_connection.close = AsyncMock()
        
        # Act
        response = client.get("/api/v1/anomalies")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]['node_id'] == 'NODE-001'
        assert data[1]['node_id'] == 'NODE-002'
        assert 'mock' not in str(data).lower()
        assert 'example' not in str(data).lower()
        assert 'generated' not in str(data).lower()
    
    async def test_never_generates_mock_data(self, client, mock_db_connection):
        """Should never generate mock data regardless of result count."""
        # Arrange - return only 1 anomaly (less than typical mock threshold)
        single_anomaly = [{
            'id': 1,
            'node_id': 'NODE-001',
            'node_name': 'Central Hub',
            'timestamp': datetime.now(timezone.utc),
            'anomaly_type': 'pressure_drop',
            'severity': 'high',
            'measurement_type': 'pressure',
            'actual_value': 1.5,
            'expected_value': 3.0,
            'deviation_percentage': 50.0,
            'description': 'Real anomaly',
            'resolved_at': None
        }]
        mock_db_connection.fetch.return_value = single_anomaly
        mock_db_connection.close = AsyncMock()
        
        # Act
        response = client.get("/api/v1/anomalies")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # Should NOT pad with mock data
        assert data[0]['description'] == 'Real anomaly'
    
    async def test_filters_work_with_real_data_only(self, client, mock_db_connection):
        """Should apply filters to real data only."""
        # Arrange
        mock_db_connection.fetch.return_value = []
        mock_db_connection.close = AsyncMock()
        
        # Act
        response = client.get("/api/v1/anomalies?severity=critical&hours=48")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []
        
        # Verify the query was called with correct parameters
        call_args = mock_db_connection.fetch.call_args
        assert call_args is not None
        assert 48 in call_args[0]  # hours parameter
        assert 'critical' in call_args[0]  # severity parameter
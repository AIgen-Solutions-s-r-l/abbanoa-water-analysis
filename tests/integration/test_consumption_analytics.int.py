"""Integration tests for consumption analytics endpoints derived from distribution data."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient


class TestConsumptionAnalyticsEndpoint:
    """Test /v1/consumption/analytics endpoint."""
    
    @pytest.fixture
    def mock_sensor_data(self):
        """Mock sensor readings data for testing."""
        return [
            {
                'timestamp': datetime.now() - timedelta(hours=24),
                'node_id': 'VIA_SANT_ANNA',
                'flow_rate': 63.61,
                'pressure': 1.64,
                'temperature': 12.0,
                'quality_score': 0.95
            },
            {
                'timestamp': datetime.now() - timedelta(hours=23),
                'node_id': 'VIA_ROMA_1', 
                'flow_rate': 124.72,
                'pressure': 2.1,
                'temperature': 11.8,
                'quality_score': 0.92
            },
            {
                'timestamp': datetime.now() - timedelta(hours=22),
                'node_id': 'PIAZZA_ITALIA_1',
                'flow_rate': 89.45,
                'pressure': 1.87,
                'temperature': 12.3,
                'quality_score': 0.97
            }
        ]
    
    @pytest.mark.asyncio
    async def test_consumption_analytics_endpoint_returns_valid_structure(self, mock_sensor_data):
        """Should return consumption analytics with expected data structure derived from sensor data."""
        # Arrange
        from src.presentation.api.app_postgres import app
        from unittest.mock import patch
        
        client = TestClient(app)
        
        # Mock database connection and query
        with patch('asyncpg.create_pool') as mock_pool:
            mock_conn = AsyncMock()
            mock_conn.fetch.return_value = mock_sensor_data
            mock_pool.return_value.acquire.return_value.__aenter__.return_value = mock_conn
            
            # Act
            response = client.get("/v1/consumption/analytics")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            # Verify expected structure for consumption analytics
            assert "summary" in data
            assert "district_consumption" in data
            assert "consumption_timeline" in data
            assert "user_segments" in data
            assert "peak_demand" in data
            assert "conservation_opportunities" in data
            assert "data_metadata" in data
            
            # Verify summary contains required fields
            summary = data["summary"]
            assert "total_daily_consumption" in summary
            assert "total_monthly_consumption" in summary  
            assert "total_users" in summary
            assert "avg_consumption_per_user" in summary
            assert "system_efficiency" in summary
            assert "water_loss_percentage" in summary
            
            # Verify data_metadata indicates derivation from sensor data
            metadata = data["data_metadata"]
            assert "data_source" in metadata
            assert metadata["data_source"] == "distribution_nodes_correlation"
            assert "synthetic_percentage" in metadata

    @pytest.mark.asyncio
    async def test_consumption_anomalies_endpoint_returns_valid_structure(self, mock_sensor_data):
        """Should return consumption anomalies derived from distribution node data."""
        # Arrange
        from src.presentation.api.app_postgres import app
        from unittest.mock import patch
        
        client = TestClient(app)
        
        # Mock database connection
        with patch('asyncpg.create_pool') as mock_pool:
            mock_conn = AsyncMock()
            mock_conn.fetch.return_value = mock_sensor_data
            mock_pool.return_value.acquire.return_value.__aenter__.return_value = mock_conn
            
            # Act
            response = client.get("/v1/consumption/anomalies")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            assert "anomalies" in data
            if data["anomalies"]:
                anomaly = data["anomalies"][0]
                assert "anomaly_id" in anomaly
                assert "type" in anomaly
                assert "severity" in anomaly
"""Integration tests for weather service transparency and data source tracking."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.servers.weather_server_prod import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestWeatherDataSourceTransparency:
    """Test weather service properly identifies data sources."""
    
    def test_current_weather_includes_data_source_field(self, client):
        """Test current weather response includes data_source field."""
        response = client.get("/weather/current")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check each location has data_source field
        for location_data in data:
            assert "data_source" in location_data
            assert location_data["data_source"] in ["real", "estimated"]
    
    def test_current_weather_marks_mock_data_as_estimated(self, client):
        """Test mock/fallback data is marked as estimated."""
        # Force mock data by not setting weather_api
        with patch('src.servers.weather_server_prod.weather_api', None):
            response = client.get("/weather/current")
            assert response.status_code == 200
            
            data = response.json()
            for location_data in data:
                assert location_data["data_source"] == "estimated"
    
    @patch('src.servers.weather_server_prod.weather_api')
    def test_current_weather_marks_real_api_data_as_real(self, mock_api, client):
        """Test real API data is marked as real."""
        # Mock successful API response
        mock_weather_data = MagicMock()
        mock_weather_data.temperature = 22.5
        mock_weather_data.humidity = 65.0
        mock_weather_data.rain_volume = 0.0
        mock_weather_data.wind_speed = 3.5
        mock_weather_data.condition = "Clear"
        
        mock_api.get_current_weather = AsyncMock(return_value=mock_weather_data)
        
        response = client.get("/weather/current")
        assert response.status_code == 200
        
        data = response.json()
        for location_data in data:
            assert location_data["data_source"] == "real"
    
    def test_current_weather_includes_last_real_update_timestamp(self, client):
        """Test response includes last_real_update timestamp."""
        response = client.get("/weather/current")
        assert response.status_code == 200
        
        data = response.json()
        for location_data in data:
            assert "last_real_update" in location_data
            # Should be either a valid ISO timestamp or null
            if location_data["last_real_update"]:
                # Verify it's a valid ISO timestamp
                datetime.fromisoformat(location_data["last_real_update"].replace('Z', '+00:00'))
    
    def test_historical_weather_includes_data_source(self, client):
        """Test historical weather includes data source information."""
        response = client.get("/weather/historical", params={
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        for day_data in data:
            assert "data_source" in day_data
            assert day_data["data_source"] in ["real", "estimated", "historical"]
    
    def test_weather_statistics_includes_data_quality_metrics(self, client):
        """Test statistics include data quality information."""
        response = client.get("/weather/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert "dataQuality" in data
        assert "realDataPercentage" in data["dataQuality"]
        assert "estimatedDataPercentage" in data["dataQuality"]
        assert "lastRealDataUpdate" in data["dataQuality"]
    
    def test_weather_status_includes_data_source_info(self, client):
        """Test status endpoint shows current data source."""
        response = client.get("/weather/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "data_source" in data
        assert "real_data_available" in data
        assert "fallback_reason" in data or data["real_data_available"]
    
    def test_impact_analysis_indicates_data_reliability(self, client):
        """Test impact analysis includes data reliability indicator."""
        response = client.get("/weather/impact-analysis")
        assert response.status_code == 200
        
        data = response.json()
        assert "dataReliability" in data
        assert data["dataReliability"] in ["high", "medium", "low"]
        assert "reliabilityNote" in data


class TestWeatherDataSourceFailover:
    """Test proper failover behavior and transparency."""
    
    @patch('src.servers.weather_server_prod.weather_api')
    def test_api_failure_triggers_estimated_data_with_message(self, mock_api, client):
        """Test API failure results in estimated data with explanation."""
        # Simulate API failure
        mock_api.get_current_weather = AsyncMock(side_effect=Exception("API Error"))
        
        response = client.get("/weather/current")
        assert response.status_code == 200
        
        data = response.json()
        for location_data in data:
            assert location_data["data_source"] == "estimated"
            assert "data_note" in location_data
            assert "API unavailable" in location_data["data_note"] or "estimated" in location_data["data_note"].lower()
    
    def test_partial_api_failure_mixed_sources(self, client):
        """Test partial API failures show mixed data sources."""
        with patch('src.servers.weather_server_prod.weather_api') as mock_api:
            # Mock API to fail for some locations
            call_count = {"count": 0}
            
            async def mock_get_weather(lat, lon):
                call_count["count"] += 1
                if call_count["count"] % 2 == 0:
                    raise Exception("API Error")
                mock_data = MagicMock()
                mock_data.temperature = 20.0
                mock_data.humidity = 60.0
                mock_data.rain_volume = 0.0
                mock_data.wind_speed = 2.0
                mock_data.condition = "Clear"
                return mock_data
            
            mock_api.get_current_weather = mock_get_weather
            
            response = client.get("/weather/current")
            assert response.status_code == 200
            
            data = response.json()
            sources = [d["data_source"] for d in data]
            # Should have both real and estimated data
            assert "real" in sources
            assert "estimated" in sources
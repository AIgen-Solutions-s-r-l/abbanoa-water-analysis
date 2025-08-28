"""
Tests for consumption API routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from src.presentation.api.consumption_routes import router
from src.infrastructure.database.consumption_service import ConsumptionService


class TestConsumptionRoutes:
    """Test suite for consumption API routes."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        return TestClient(app)
    
    @pytest.fixture
    def mock_consumption_service(self):
        """Create mock consumption service."""
        return Mock(spec=ConsumptionService)
    
    def test_get_consumption_analytics_returns_200(self, client, mock_consumption_service):
        """Test that GET /api/v1/consumption/analytics returns 200."""
        # Arrange
        mock_data = {
            "data_metadata": {
                "total_readings": 41704,
                "active_nodes": 7,
                "is_real_time": False,
                "data_source": "Historical Database"
            },
            "summary": {
                "total_daily_consumption": 1500000,
                "total_users": 100000,
                "avg_consumption_per_user": 15.0
            }
        }
        mock_consumption_service.get_consumption_analytics.return_value = mock_data
        
        with patch('src.presentation.api.consumption_routes.get_consumption_service', return_value=mock_consumption_service):
            # Act
            response = client.get("/api/v1/consumption/analytics")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "data_metadata" in data
            assert "summary" in data
            assert data["data_metadata"]["total_readings"] == 41704
            assert data["data_metadata"]["active_nodes"] == 7
    
    def test_get_consumption_analytics_returns_real_data_structure(self, client, mock_consumption_service):
        """Test that GET /api/v1/consumption/analytics returns correct data structure."""
        # Arrange
        mock_data = {
            "data_metadata": {
                "latest_timestamp": "2025-06-19T05:30:00+00:00",
                "earliest_timestamp": "2024-11-14T00:00:00+00:00",
                "total_readings": 41704,
                "flow_readings": 41704,
                "synthetic_percentage": 0.0,
                "data_age_hours": 2.5,
                "active_nodes": 7,
                "is_real_time": False,
                "data_source": "Historical Database"
            },
            "summary": {
                "total_daily_consumption": 1500000,
                "total_monthly_consumption": 45000000,
                "total_users": 100000,
                "avg_consumption_per_user": 15.0,
                "system_efficiency": 0.92,
                "water_loss_percentage": 8
            },
            "district_consumption": [
                {
                    "district_id": "VIA_DANTE_1",
                    "district_name": "Via Dante Principale",
                    "node_type": "main",
                    "total_users": 25000,
                    "daily_consumption_liters": 375000,
                    "monthly_consumption_liters": 11250000,
                    "avg_per_user_daily": 15.0,
                    "peak_hour": 8,
                    "efficiency_score": 0.92
                }
            ],
            "consumption_timeline": [
                {
                    "timestamp": "2025-06-19T00:00:00",
                    "consumption_liters": 62500,
                    "forecast_consumption": 65625
                }
            ],
            "user_segments": [
                {
                    "segment": "Residential",
                    "user_count": 75000,
                    "percentage": 75,
                    "avg_daily_consumption": 250,
                    "trend": "stable"
                }
            ],
            "peak_demand": {
                "daily_peak_time": "08:00",
                "daily_peak_consumption": 75000,
                "weekly_peak_day": "Monday",
                "monthly_peak_date": "2025-06-15",
                "seasonal_peak_month": "August"
            },
            "conservation_opportunities": [
                {
                    "opportunity": "Leak Detection Program",
                    "potential_savings_liters_daily": 30000,
                    "potential_savings_percentage": 2,
                    "implementation_cost": "Medium",
                    "roi_months": 12
                }
            ]
        }
        mock_consumption_service.get_consumption_analytics.return_value = mock_data
        
        with patch('src.presentation.api.consumption_routes.get_consumption_service', return_value=mock_consumption_service):
            # Act
            response = client.get("/api/v1/consumption/analytics")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            # Verify all required sections are present
            assert "data_metadata" in data
            assert "summary" in data
            assert "district_consumption" in data
            assert "consumption_timeline" in data
            assert "user_segments" in data
            assert "peak_demand" in data
            assert "conservation_opportunities" in data
            
            # Verify data types and structure
            assert isinstance(data["data_metadata"]["total_readings"], int)
            assert isinstance(data["summary"]["total_daily_consumption"], (int, float))
            assert isinstance(data["district_consumption"], list)
            assert isinstance(data["consumption_timeline"], list)
            assert isinstance(data["user_segments"], list)
    
    def test_get_consumption_analytics_handles_service_errors(self, client, mock_consumption_service):
        """Test that GET /api/v1/consumption/analytics handles service errors gracefully."""
        # Arrange
        mock_consumption_service.get_consumption_analytics.side_effect = Exception("Database error")
        
        with patch('src.presentation.api.consumption_routes.get_consumption_service', return_value=mock_consumption_service):
            # Act
            response = client.get("/api/v1/consumption/analytics")
            
            # Assert
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "Database error" in data["error"]
    
    def test_get_consumption_analytics_returns_real_date_range(self, client, mock_consumption_service):
        """Test that GET /api/v1/consumption/analytics returns realistic date range."""
        # Arrange
        mock_data = {
            "data_metadata": {
                "latest_timestamp": "2025-06-19T05:30:00+00:00",
                "earliest_timestamp": "2024-11-14T00:00:00+00:00",
                "total_readings": 41704,
                "active_nodes": 7,
                "is_real_time": False,
                "data_source": "Historical Database"
            },
            "summary": {
                "total_daily_consumption": 1500000,
                "total_users": 100000,
                "avg_consumption_per_user": 15.0
            }
        }
        mock_consumption_service.get_consumption_analytics.return_value = mock_data
        
        with patch('src.presentation.api.consumption_routes.get_consumption_service', return_value=mock_consumption_service):
            # Act
            response = client.get("/api/v1/consumption/analytics")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            # Verify date range is realistic
            earliest = datetime.fromisoformat(data["data_metadata"]["earliest_timestamp"].replace('Z', '+00:00'))
            latest = datetime.fromisoformat(data["data_metadata"]["latest_timestamp"].replace('Z', '+00:00'))
            
            assert earliest.year == 2024
            assert latest.year == 2025
            assert earliest < latest
    
    def test_get_consumption_analytics_returns_real_node_data(self, client, mock_consumption_service):
        """Test that GET /api/v1/consumption/analytics returns real node data."""
        # Arrange
        mock_data = {
            "data_metadata": {
                "total_readings": 41704,
                "active_nodes": 7,
                "is_real_time": False,
                "data_source": "Historical Database"
            },
            "district_consumption": [
                {
                    "district_id": "VIA_DANTE_1",
                    "district_name": "Via Dante Principale",
                    "node_type": "main"
                },
                {
                    "district_id": "VIA_ROMA_1",
                    "district_name": "Via Roma Secondario",
                    "node_type": "secondary"
                }
            ],
            "summary": {
                "total_daily_consumption": 1500000,
                "total_users": 100000,
                "avg_consumption_per_user": 15.0
            }
        }
        mock_consumption_service.get_consumption_analytics.return_value = mock_data
        
        with patch('src.presentation.api.consumption_routes.get_consumption_service', return_value=mock_consumption_service):
            # Act
            response = client.get("/api/v1/consumption/analytics")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            # Verify node names match real infrastructure
            node_names = [node["district_name"] for node in data["district_consumption"]]
            expected_nodes = [
                "Via Dante Principale",
                "Via Roma Secondario"
            ]
            
            for expected in expected_nodes:
                assert expected in node_names

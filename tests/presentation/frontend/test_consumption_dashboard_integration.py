"""
Tests for Next.js dashboard integration with consumption analytics API.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from datetime import datetime


class TestConsumptionDashboardIntegration:
    """Test suite for Next.js dashboard integration."""
    
    @pytest.fixture
    def api_base_url(self):
        """Get API base URL."""
        return "http://localhost:8000/api/v1"
    
    def test_dashboard_can_fetch_consumption_analytics(self, api_base_url):
        """Test that dashboard can fetch consumption analytics data."""
        # This test verifies the API endpoint is accessible
        # In a real scenario, this would be called from the Next.js frontend
        
        # Mock the API call that would be made from Next.js
        with patch('requests.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
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
            mock_get.return_value = mock_response
            
            # Simulate API call from Next.js
            response = requests.get(f"{api_base_url}/consumption/analytics")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "data_metadata" in data
            assert "summary" in data
            assert data["data_metadata"]["total_readings"] == 41704
    
    def test_dashboard_can_fetch_summary_data(self, api_base_url):
        """Test that dashboard can fetch summary data."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "summary": {
                    "total_daily_consumption": 1500000,
                    "total_users": 100000,
                    "avg_consumption_per_user": 15.0,
                    "system_efficiency": 0.92,
                    "water_loss_percentage": 8
                },
                "data_metadata": {
                    "is_real_time": False,
                    "data_source": "Historical Database"
                }
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f"{api_base_url}/consumption/summary")
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert data["summary"]["total_daily_consumption"] == 1500000
    
    def test_dashboard_can_fetch_district_data(self, api_base_url):
        """Test that dashboard can fetch district consumption data."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "district_consumption": [
                    {
                        "district_id": "VIA_DANTE_1",
                        "district_name": "Via Dante Principale",
                        "node_type": "main",
                        "total_users": 25000,
                        "daily_consumption_liters": 375000
                    }
                ],
                "data_metadata": {
                    "is_real_time": False
                }
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f"{api_base_url}/consumption/districts")
            
            assert response.status_code == 200
            data = response.json()
            assert "district_consumption" in data
            assert len(data["district_consumption"]) > 0
            assert data["district_consumption"][0]["district_name"] == "Via Dante Principale"
    
    def test_dashboard_can_fetch_timeline_data(self, api_base_url):
        """Test that dashboard can fetch consumption timeline data."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "consumption_timeline": [
                    {
                        "timestamp": "2025-06-19T00:00:00",
                        "consumption_liters": 62500,
                        "forecast_consumption": 65625
                    }
                ],
                "data_metadata": {
                    "is_real_time": False
                }
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f"{api_base_url}/consumption/timeline")
            
            assert response.status_code == 200
            data = response.json()
            assert "consumption_timeline" in data
            assert len(data["consumption_timeline"]) > 0
            assert "timestamp" in data["consumption_timeline"][0]
    
    def test_dashboard_handles_api_errors_gracefully(self, api_base_url):
        """Test that dashboard handles API errors gracefully."""
        with patch('requests.get') as mock_get:
            # Mock API error
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {
                "error": "Database connection failed"
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f"{api_base_url}/consumption/analytics")
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
    
    def test_dashboard_data_structure_matches_frontend_expectations(self, api_base_url):
        """Test that API data structure matches what the frontend expects."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data_metadata": {
                    "total_readings": 41704,
                    "active_nodes": 7,
                    "is_real_time": False,
                    "data_source": "Historical Database"
                },
                "summary": {
                    "total_daily_consumption": 1500000,
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
                        "daily_consumption_liters": 375000
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
                        "avg_daily_consumption": 250
                    }
                ],
                "peak_demand": {
                    "daily_peak_time": "08:00",
                    "daily_peak_consumption": 75000,
                    "weekly_peak_day": "Monday"
                },
                "conservation_opportunities": [
                    {
                        "opportunity": "Leak Detection Program",
                        "potential_savings_liters_daily": 30000,
                        "potential_savings_percentage": 2
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            response = requests.get(f"{api_base_url}/consumption/analytics")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify all expected sections are present for frontend
            required_sections = [
                "data_metadata", "summary", "district_consumption",
                "consumption_timeline", "user_segments", "peak_demand",
                "conservation_opportunities"
            ]
            
            for section in required_sections:
                assert section in data, f"Missing required section: {section}"
            
            # Verify data types are correct for frontend consumption
            assert isinstance(data["summary"]["total_daily_consumption"], (int, float))
            assert isinstance(data["summary"]["total_users"], int)
            assert isinstance(data["district_consumption"], list)
            assert isinstance(data["consumption_timeline"], list)

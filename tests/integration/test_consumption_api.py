"""
Integration tests for Consumption API endpoints.

Tests complete request/response cycles for all consumption-related endpoints.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json

# Mock the main application for testing
from unittest.mock import MagicMock
mock_app = MagicMock()

@pytest.mark.integration
@pytest.mark.consumption
class TestConsumptionAPIIntegration:
    """Integration test suite for Consumption API."""

    @pytest.fixture
    def mock_app(self):
        """Provide mocked FastAPI app."""
        return mock_app

    @pytest.fixture
    def test_client(self, mock_app):
        """Provide test client."""
        return TestClient(mock_app)

    @pytest.fixture
    def sample_consumption_response(self):
        """Sample consumption API response."""
        return {
            "data": [
                {
                    "node_id": "NODE_001",
                    "timestamp": "2024-01-01T10:00:00Z",
                    "consumption_value": 150.0,
                    "region": "North",
                    "unit": "liters"
                },
                {
                    "node_id": "NODE_002",
                    "timestamp": "2024-01-01T11:00:00Z",
                    "consumption_value": 200.0,
                    "region": "South", 
                    "unit": "liters"
                }
            ],
            "metadata": {
                "total_count": 2,
                "page_count": 1,
                "current_page": 1,
                "page_size": 50,
                "has_next_page": False,
                "has_previous_page": False
            },
            "execution_time_ms": 150.5
        }

    @pytest.mark.asyncio
    async def test_get_consumption_data_endpoint(
        self, test_client, sample_consumption_response, api_test_utils
    ):
        """Test GET /consumption/data endpoint."""
        # Mock the endpoint response
        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_consumption_response

            response = test_client.get(
                "/consumption/data",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z",
                    "page": 1,
                    "page_size": 50
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Test response structure
            api_test_utils.assert_valid_response_structure(
                data, ["data", "metadata", "execution_time_ms"]
            )

            # Test pagination metadata
            api_test_utils.assert_pagination_metadata(data["metadata"])

            # Test data content
            assert len(data["data"]) == 2
            for item in data["data"]:
                assert "node_id" in item
                assert "consumption_value" in item
                assert "timestamp" in item
                api_test_utils.assert_datetime_format(item["timestamp"])

    @pytest.mark.asyncio
    async def test_get_consumption_analytics_endpoint(
        self, test_client, api_test_utils
    ):
        """Test GET /consumption/analytics endpoint."""
        sample_analytics = {
            "total_consumption": 2500.0,
            "average_consumption": 125.0,
            "peak_consumption": 300.0,
            "consumption_trend": "increasing",
            "top_consumers": [
                {"node_id": "NODE_001", "consumption": 500.0},
                {"node_id": "NODE_002", "consumption": 450.0}
            ],
            "consumption_by_region": {
                "North": 1200.0,
                "South": 1300.0
            },
            "execution_time_ms": 89.3
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_analytics

            response = test_client.get(
                "/consumption/analytics",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Test analytics structure
            required_fields = [
                "total_consumption", "average_consumption", "peak_consumption",
                "consumption_trend", "top_consumers", "consumption_by_region"
            ]
            api_test_utils.assert_valid_response_structure(data, required_fields)

            # Test data types
            assert isinstance(data["total_consumption"], (int, float))
            assert isinstance(data["average_consumption"], (int, float))
            assert isinstance(data["top_consumers"], list)
            assert isinstance(data["consumption_by_region"], dict)

    @pytest.mark.asyncio
    async def test_get_node_consumption_endpoint(
        self, test_client, api_test_utils
    ):
        """Test GET /consumption/node/{node_id} endpoint."""
        node_id = "NODE_001"
        sample_node_data = {
            "node_id": node_id,
            "data": [
                {
                    "timestamp": "2024-01-01T10:00:00Z",
                    "consumption_value": 150.0,
                    "hourly_average": 140.0,
                    "daily_total": 3360.0
                }
            ],
            "statistics": {
                "total_consumption": 3360.0,
                "average_consumption": 140.0,
                "peak_consumption": 180.0,
                "consumption_trend": "stable"
            },
            "execution_time_ms": 45.2
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_node_data

            response = test_client.get(
                f"/consumption/node/{node_id}",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Test node data structure
            api_test_utils.assert_valid_response_structure(
                data, ["node_id", "data", "statistics"]
            )

            assert data["node_id"] == node_id
            assert isinstance(data["data"], list)
            assert isinstance(data["statistics"], dict)

    @pytest.mark.asyncio
    async def test_get_consumption_trends_endpoint(
        self, test_client, api_test_utils
    ):
        """Test GET /consumption/trends endpoint."""
        sample_trends = {
            "trends": [
                {
                    "period": "2024-01-01",
                    "consumption_value": 2500.0,
                    "trend_direction": "increasing",
                    "change_percentage": 5.2,
                    "seasonal_adjustment": 0.95
                },
                {
                    "period": "2024-01-02",
                    "consumption_value": 2600.0,
                    "trend_direction": "increasing",
                    "change_percentage": 4.0,
                    "seasonal_adjustment": 1.02
                }
            ],
            "overall_trend": {
                "direction": "increasing",
                "strength": "moderate",
                "confidence": 0.87
            },
            "execution_time_ms": 67.8
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_trends

            response = test_client.get(
                "/consumption/trends",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-07T23:59:59Z",
                    "resolution": "daily"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Test trends structure
            api_test_utils.assert_valid_response_structure(
                data, ["trends", "overall_trend"]
            )

            assert isinstance(data["trends"], list)
            assert len(data["trends"]) == 2
            
            for trend in data["trends"]:
                assert "period" in trend
                assert "consumption_value" in trend
                assert "trend_direction" in trend

    @pytest.mark.asyncio
    async def test_detect_consumption_anomalies_endpoint(
        self, test_client, api_test_utils
    ):
        """Test GET /consumption/anomalies endpoint."""
        sample_anomalies = {
            "anomalies": [
                {
                    "node_id": "NODE_001",
                    "timestamp": "2024-01-01T14:00:00Z",
                    "consumption_value": 500.0,
                    "expected_value": 150.0,
                    "anomaly_type": "spike",
                    "severity": "high",
                    "confidence_score": 0.95,
                    "description": "Consumption spike detected - 233% above normal"
                }
            ],
            "summary": {
                "total_anomalies": 1,
                "high_severity": 1,
                "medium_severity": 0,
                "low_severity": 0
            },
            "execution_time_ms": 234.1
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_anomalies

            response = test_client.get(
                "/consumption/anomalies",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z",
                    "sensitivity": "medium"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Test anomalies structure
            api_test_utils.assert_valid_response_structure(
                data, ["anomalies", "summary"]
            )

            assert isinstance(data["anomalies"], list)
            if data["anomalies"]:
                anomaly = data["anomalies"][0]
                assert "node_id" in anomaly
                assert "anomaly_type" in anomaly
                assert "severity" in anomaly
                assert "confidence_score" in anomaly

    @pytest.mark.asyncio
    async def test_get_consumption_forecast_endpoint(
        self, test_client, api_test_utils
    ):
        """Test GET /consumption/forecast endpoint."""
        sample_forecast = {
            "forecasts": [
                {
                    "node_id": "NODE_001",
                    "forecast_date": "2024-01-02T00:00:00Z",
                    "predicted_consumption": 145.0,
                    "confidence_interval": [130.0, 160.0],
                    "model_type": "arima",
                    "accuracy_score": 0.92
                }
            ],
            "model_info": {
                "model_type": "arima",
                "training_period": "30_days",
                "accuracy": 0.92,
                "last_updated": "2024-01-01T20:00:00Z"
            },
            "execution_time_ms": 156.7
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_forecast

            response = test_client.get(
                "/consumption/forecast",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z",
                    "forecast_days": 7
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Test forecast structure
            api_test_utils.assert_valid_response_structure(
                data, ["forecasts", "model_info"]
            )

            assert isinstance(data["forecasts"], list)
            if data["forecasts"]:
                forecast = data["forecasts"][0]
                assert "node_id" in forecast
                assert "predicted_consumption" in forecast
                assert "confidence_interval" in forecast

    @pytest.mark.asyncio
    async def test_get_optimization_suggestions_endpoint(
        self, test_client, api_test_utils
    ):
        """Test GET /consumption/optimization endpoint."""
        sample_optimization = {
            "suggestions": [
                {
                    "node_id": "NODE_001",
                    "suggestion_type": "reduce_consumption",
                    "priority": "high",
                    "description": "High consumption detected - consider pressure optimization",
                    "potential_savings": 15.5,
                    "implementation_effort": "medium",
                    "estimated_cost": 5000.0
                }
            ],
            "summary": {
                "total_suggestions": 1,
                "high_priority": 1,
                "medium_priority": 0,
                "low_priority": 0,
                "total_potential_savings": 15.5
            },
            "execution_time_ms": 98.4
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_optimization

            response = test_client.get(
                "/consumption/optimization",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Test optimization structure
            api_test_utils.assert_valid_response_structure(
                data, ["suggestions", "summary"]
            )

            assert isinstance(data["suggestions"], list)
            if data["suggestions"]:
                suggestion = data["suggestions"][0]
                assert "node_id" in suggestion
                assert "suggestion_type" in suggestion
                assert "priority" in suggestion

    @pytest.mark.asyncio
    async def test_consumption_api_error_handling(self, test_client):
        """Test error handling in consumption API."""
        # Test invalid date format
        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 422
            mock_get.return_value.json.return_value = {
                "detail": [
                    {
                        "loc": ["query", "start_time"],
                        "msg": "invalid datetime format",
                        "type": "value_error.datetime"
                    }
                ]
            }

            response = test_client.get(
                "/consumption/data",
                params={
                    "start_time": "invalid-date",
                    "end_time": "2024-01-01T23:59:59Z"
                }
            )

            assert response.status_code == 422
            data = response.json()
            assert "detail" in data

        # Test missing required parameters
        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 422
            mock_get.return_value.json.return_value = {
                "detail": [
                    {
                        "loc": ["query", "start_time"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }

            response = test_client.get("/consumption/data")

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_consumption_api_pagination(self, test_client, api_test_utils):
        """Test pagination in consumption API."""
        # Test first page
        first_page_response = {
            "data": [{"node_id": f"NODE_{i:03d}", "consumption_value": i * 10} for i in range(50)],
            "metadata": {
                "total_count": 150,
                "page_count": 3,
                "current_page": 1,
                "page_size": 50,
                "has_next_page": True,
                "has_previous_page": False
            }
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = first_page_response

            response = test_client.get(
                "/consumption/data",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z",
                    "page": 1,
                    "page_size": 50
                }
            )

            assert response.status_code == 200
            data = response.json()

            api_test_utils.assert_pagination_metadata(data["metadata"])
            assert data["metadata"]["current_page"] == 1
            assert data["metadata"]["has_next_page"] is True
            assert data["metadata"]["has_previous_page"] is False

    @pytest.mark.asyncio
    async def test_consumption_api_filtering(self, test_client):
        """Test filtering in consumption API."""
        filtered_response = {
            "data": [
                {
                    "node_id": "NODE_001",
                    "consumption_value": 150.0,
                    "region": "North"
                }
            ],
            "metadata": {
                "total_count": 1,
                "page_count": 1,
                "current_page": 1,
                "page_size": 50,
                "has_next_page": False,
                "has_previous_page": False
            },
            "filter_applied": {
                "selected_nodes": ["NODE_001"],
                "region": "North"
            }
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = filtered_response

            response = test_client.get(
                "/consumption/data",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z",
                    "selected_nodes": ["NODE_001"],
                    "region": "North"
                }
            )

            assert response.status_code == 200
            data = response.json()

            assert len(data["data"]) == 1
            assert data["data"][0]["node_id"] == "NODE_001"
            assert data["data"][0]["region"] == "North"

    @pytest.mark.asyncio
    async def test_consumption_api_performance(
        self, test_client, api_test_utils, test_performance_config
    ):
        """Test consumption API performance."""
        # Large dataset response
        large_response = {
            "data": [
                {"node_id": f"NODE_{i:03d}", "consumption_value": i * 10}
                for i in range(1000)
            ],
            "metadata": {
                "total_count": 1000,
                "page_count": 20,
                "current_page": 1,
                "page_size": 50,
                "has_next_page": True,
                "has_previous_page": False
            },
            "execution_time_ms": 2500.0  # Within acceptable range
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = large_response

            response = test_client.get(
                "/consumption/data",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z",
                    "page_size": 50
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Test performance metrics
            api_test_utils.assert_performance_metrics(
                data, test_performance_config["max_response_time_ms"]
            )

    @pytest.mark.asyncio
    async def test_consumption_api_data_validation(self, test_client):
        """Test data validation in consumption API responses."""
        sample_response = {
            "data": [
                {
                    "node_id": "NODE_001",
                    "timestamp": "2024-01-01T10:00:00Z",
                    "consumption_value": 150.0,
                    "region": "North",
                    "unit": "liters"
                }
            ],
            "metadata": {
                "total_count": 1,
                "page_count": 1,
                "current_page": 1,
                "page_size": 50,
                "has_next_page": False,
                "has_previous_page": False
            }
        }

        with patch.object(test_client, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = sample_response

            response = test_client.get(
                "/consumption/data",
                params={
                    "start_time": "2024-01-01T00:00:00Z",
                    "end_time": "2024-01-01T23:59:59Z"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Validate data structure
            for item in data["data"]:
                assert isinstance(item["node_id"], str)
                assert isinstance(item["consumption_value"], (int, float))
                assert item["consumption_value"] >= 0  # Non-negative consumption
                assert isinstance(item["region"], str)
                assert item["unit"] in ["liters", "cubic_meters", "gallons"] 
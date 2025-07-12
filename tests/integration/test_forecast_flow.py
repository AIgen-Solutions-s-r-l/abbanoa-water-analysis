"""Integration tests for the complete forecast flow."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.application.use_cases.forecast_consumption import ForecastConsumption
from src.infrastructure.clients.async_bigquery_client import AsyncBigQueryClient
from src.infrastructure.repositories.bigquery_forecast_repository import (
    BigQueryForecastRepository,
)
from src.infrastructure.services.forecast_calculation_service import (
    ForecastCalculationService,
)
from src.presentation.api.app import app


class TestForecastIntegration:
    """Integration tests for forecast functionality."""

    @pytest.fixture
    def test_client(self):
        """Create test client for API."""
        return TestClient(app)

    @pytest.fixture
    def mock_bigquery_client(self):
        """Create mock BigQuery client."""
        client = MagicMock(spec=AsyncBigQueryClient)
        client.project_id = "test-project"
        client.dataset_id = "test-dataset"
        client.ml_dataset_id = "ml_models"
        return client

    @pytest.fixture
    def sample_historical_data(self):
        """Create sample historical data."""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30), end=datetime.now(), freq="D"
        )
        return pd.DataFrame(
            {
                "timestamp": dates,
                "value": [100 + i * 0.5 + (i % 7) * 2 for i in range(len(dates))],
                "district_id": "DIST_001",
                "metric": "flow_rate",
            }
        )

    @pytest.fixture
    def sample_forecast_data(self):
        """Create sample forecast data."""
        dates = pd.date_range(
            start=datetime.now() + timedelta(days=1), periods=7, freq="D"
        )
        values = [105 + i * 0.3 for i in range(7)]
        return pd.DataFrame(
            {
                "timestamp": dates,
                "value": values,
                "lower_bound": [v - 5 for v in values],
                "upper_bound": [v + 5 for v in values],
                "district_id": "DIST_001",
                "metric": "flow_rate",
                "standard_error": 2.5,
                "confidence_level": 0.8,
            }
        )

    @pytest.mark.asyncio
    async def test_forecast_calculation_service_success(
        self, mock_bigquery_client, sample_historical_data, sample_forecast_data
    ):
        """Test successful forecast calculation."""
        # Mock BigQuery responses
        mock_bigquery_client.query_to_dataframe = AsyncMock(
            side_effect=[sample_historical_data, sample_forecast_data]
        )

        # Create service
        service = ForecastCalculationService(mock_bigquery_client)

        # Execute forecast
        result = await service.calculate_forecast(
            district_id="DIST_001",
            metric="flow_rate",
            horizon=7,
            include_history_days=30,
        )

        # Verify results
        assert "historical" in result
        assert "forecast" in result
        assert "metrics" in result
        assert "metadata" in result

        assert len(result["historical"]) == 31
        assert len(result["forecast"]) == 7

        # Check metrics
        assert result["metrics"]["trend_direction"] in [
            "increasing",
            "decreasing",
            "stable",
        ]
        assert 0 <= result["metrics"]["trend_strength"] <= 1
        assert result["metrics"]["forecast_mean"] > 0

    @pytest.mark.asyncio
    async def test_forecast_calculation_service_fallback(self, mock_bigquery_client):
        """Test fallback mechanism when ML forecast fails."""
        # Mock historical data success, forecast failure
        historical_data = pd.DataFrame(
            {
                "timestamp": pd.date_range(start="2024-01-01", periods=30),
                "value": [100] * 30,
                "district_id": "DIST_001",
                "metric": "flow_rate",
            }
        )

        mock_bigquery_client.query_to_dataframe = AsyncMock(
            side_effect=[historical_data, Exception("ML.FORECAST failed")]
        )

        # Create service
        service = ForecastCalculationService(mock_bigquery_client)

        # Execute forecast - should use fallback
        result = await service.calculate_forecast(
            district_id="DIST_001", metric="flow_rate", horizon=7
        )

        # Verify fallback results
        assert result["metadata"].get("fallback") is True
        assert len(result["forecast"]) == 7
        assert result["forecast"]["value"].iloc[0] == 100  # Simple average

    @pytest.mark.asyncio
    async def test_forecast_repository_integration(
        self, mock_bigquery_client, sample_forecast_data
    ):
        """Test forecast repository integration."""
        # Mock model exists check
        mock_bigquery_client.execute_query = AsyncMock(
            return_value=pd.DataFrame({"exists": [1]})
        )
        mock_bigquery_client.query_to_dataframe = AsyncMock(
            return_value=sample_forecast_data
        )

        # Create repository
        repository = BigQueryForecastRepository(mock_bigquery_client)

        # Get forecast
        result = await repository.get_model_forecast(
            model_name="arima_dist_001_flow_rate",
            district_metric_id="DIST_001_flow_rate",
            horizon=7,
        )

        assert len(result) == 7
        assert "timestamp" in result.columns
        assert "forecast_value" in result.columns

    @pytest.mark.asyncio
    async def test_forecast_use_case_with_calculations(
        self, mock_bigquery_client, sample_historical_data, sample_forecast_data
    ):
        """Test forecast use case with calculation service."""
        # Setup mocks
        mock_bigquery_client.query_to_dataframe = AsyncMock(
            side_effect=[sample_historical_data, sample_forecast_data]
        )

        # Create components
        repository = BigQueryForecastRepository(mock_bigquery_client)
        calc_service = ForecastCalculationService(mock_bigquery_client)
        use_case = ForecastConsumption(repository, calc_service)

        # Execute forecast with calculations
        result = await use_case.get_forecast_with_calculations(
            district_id="DIST_001",
            metric="flow_rate",
            horizon=7,
            include_historical=True,
            historical_days=30,
        )

        # Verify complete result
        assert "forecast" in result
        assert "historical" in result
        assert "metrics" in result
        assert "metadata" in result

        # Check data consistency
        forecast_df = result["forecast"]
        assert "forecast_value" in forecast_df.columns
        assert "district_id" in forecast_df.columns
        assert forecast_df["district_id"].iloc[0] == "DIST_001"

    def test_api_endpoint_success(self, test_client):
        """Test forecast API endpoint."""
        with patch(
            "src.presentation.api.endpoints.forecast_endpoint.AsyncBigQueryClient"
        ) as mock_client_class:
            # Mock the client instance
            mock_client = MagicMock()
            mock_client.project_id = "test-project"
            mock_client.dataset_id = "test-dataset"
            mock_client.ml_dataset_id = "ml_models"

            # Mock forecast data
            forecast_data = pd.DataFrame(
                {
                    "timestamp": pd.date_range("2024-01-01", periods=7),
                    "value": [100 + i for i in range(7)],
                    "lower_bound": [95 + i for i in range(7)],
                    "upper_bound": [105 + i for i in range(7)],
                    "confidence_level": 0.8,
                }
            )

            mock_client.query_to_dataframe = AsyncMock(return_value=forecast_data)

            mock_client_class.return_value = mock_client

            # Call API
            response = test_client.get("/api/v1/forecasts/DIST_001/flow_rate?horizon=7")

            assert response.status_code == 200
            data = response.json()

            assert data["district_id"] == "DIST_001"
            assert data["metric"] == "flow_rate"
            assert data["horizon"] == 7
            assert len(data["forecast_data"]) == 7

    def test_api_endpoint_invalid_district(self, test_client):
        """Test API with invalid district."""
        response = test_client.get("/api/v1/forecasts/INVALID/flow_rate")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid district_id" in data["detail"]

    def test_api_endpoint_invalid_metric(self, test_client):
        """Test API with invalid metric."""
        response = test_client.get("/api/v1/forecasts/DIST_001/invalid_metric")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid metric" in data["detail"]

    @pytest.mark.asyncio
    async def test_end_to_end_forecast_flow(self, mock_bigquery_client):
        """Test complete end-to-end forecast flow."""
        # Setup comprehensive mocks
        historical_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=30),
                "value": [100 + i * 0.5 for i in range(30)],
                "district_id": "DIST_001",
                "metric": "flow_rate",
            }
        )

        forecast_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-31", periods=7),
                "value": [115 + i * 0.3 for i in range(7)],
                "lower_bound": [110 + i * 0.3 for i in range(7)],
                "upper_bound": [120 + i * 0.3 for i in range(7)],
                "standard_error": 2.5,
                "confidence_level": 0.8,
            }
        )

        mock_bigquery_client.query_to_dataframe = AsyncMock(
            side_effect=[historical_data, forecast_data]
        )

        # Create full pipeline
        calc_service = ForecastCalculationService(mock_bigquery_client)
        repository = BigQueryForecastRepository(mock_bigquery_client)
        use_case = ForecastConsumption(repository, calc_service)

        # Execute
        result = await use_case.get_forecast_with_calculations(
            district_id="DIST_001", metric="flow_rate", horizon=7
        )

        # Comprehensive validation
        assert result["metadata"]["method"] != "fallback"
        assert result["metrics"]["forecast_mean"] > 100
        assert result["metrics"]["trend_direction"] == "increasing"
        assert len(result["forecast"]) == 7
        assert len(result["historical"]) == 30

        # Validate data quality
        forecast_df = result["forecast"]
        assert forecast_df["lower_bound"].lt(forecast_df["value"]).all()
        assert forecast_df["upper_bound"].gt(forecast_df["value"]).all()
        assert forecast_df["confidence_level"].eq(0.8).all()

    @pytest.mark.asyncio
    async def test_concurrent_forecast_requests(self, mock_bigquery_client):
        """Test handling multiple concurrent forecast requests."""
        # Setup mock
        mock_bigquery_client.query_to_dataframe = AsyncMock(
            return_value=pd.DataFrame(
                {
                    "timestamp": pd.date_range("2024-01-01", periods=7),
                    "value": [100] * 7,
                    "lower_bound": [95] * 7,
                    "upper_bound": [105] * 7,
                    "standard_error": 2.5,
                }
            )
        )

        service = ForecastCalculationService(mock_bigquery_client)

        # Execute multiple forecasts concurrently
        tasks = [
            service.calculate_forecast("DIST_001", "flow_rate", 7),
            service.calculate_forecast("DIST_001", "pressure", 7),
            service.calculate_forecast("DIST_002", "flow_rate", 7),
        ]

        results = await asyncio.gather(*tasks)

        # Verify all completed successfully
        assert len(results) == 3
        for result in results:
            assert "forecast" in result
            assert len(result["forecast"]) == 7

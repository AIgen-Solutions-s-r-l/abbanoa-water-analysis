"""
Unit tests for ForecastConsumption use case.

Tests the business logic for forecast retrieval with mocked dependencies,
ensuring proper validation, error handling, and response formatting.
"""

import logging
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from src.application.use_cases.forecast_consumption import (
    ForecastConsumption,
    MetricsCollector,
)
from src.domain.value_objects.forecast_request import ForecastRequest
from src.domain.value_objects.forecast_response import ForecastResponse
from src.shared.exceptions.forecast_exceptions import (
    ForecastNotFoundException,
    ForecastServiceException,
    InvalidForecastRequestException,
)


@pytest.fixture
def mock_repository():
    """Create mock forecast repository."""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return MagicMock(spec=logging.Logger)


@pytest.fixture
def mock_metrics():
    """Create mock metrics collector."""
    return MagicMock(spec=MetricsCollector)


@pytest.fixture
def forecast_use_case(mock_repository, mock_logger, mock_metrics):
    """Create ForecastConsumption instance with mocked dependencies."""
    return ForecastConsumption(
        forecast_repository=mock_repository, logger=mock_logger, metrics=mock_metrics
    )


@pytest.fixture
def sample_forecast_df():
    """Create sample forecast DataFrame."""
    data = {
        "timestamp": pd.date_range(start="2025-07-05", periods=7, freq="D", tz="UTC"),
        "forecast_value": [100.5, 102.3, 101.8, 103.2, 104.1, 102.9, 101.7],
        "lower_bound": [95.0, 96.5, 95.8, 97.1, 97.9, 96.7, 95.5],
        "upper_bound": [106.0, 108.1, 107.8, 109.3, 110.3, 109.1, 107.9],
        "confidence_level": [0.95] * 7,
    }
    return pd.DataFrame(data)


class TestForecastConsumption:
    """Test suite for ForecastConsumption use case."""

    @pytest.mark.asyncio
    async def test_get_forecast_valid_request(
        self, forecast_use_case, mock_repository, sample_forecast_df, mock_metrics
    ):
        """Test successful forecast retrieval with valid parameters."""
        # Arrange
        district_id = "DIST_001"
        metric = "flow_rate"
        horizon = 7

        mock_repository.get_model_forecast.return_value = sample_forecast_df

        # Act
        result = await forecast_use_case.get_forecast(
            district_id=district_id, metric=metric, horizon=horizon
        )

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 7
        assert list(result.columns) == [
            "timestamp",
            "district_id",
            "metric",
            "forecast_value",
            "lower_bound",
            "upper_bound",
            "confidence_level",
        ]
        assert (result["district_id"] == district_id).all()
        assert (result["metric"] == metric).all()
        assert result["timestamp"].dt.tz is not None  # Timezone aware

        # Verify repository called correctly
        mock_repository.get_model_forecast.assert_called_once_with(
            model_name=f"arima_{district_id.lower()}_{metric}",
            district_metric_id=f"{district_id}_{metric}",
            horizon=horizon,
        )

        # Verify metrics recorded
        mock_metrics.record_count.assert_called_once()
        mock_metrics.record_latency.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_forecast_invalid_district_id(
        self, forecast_use_case, mock_repository
    ):
        """Test error handling for invalid district ID."""
        # Act & Assert
        with pytest.raises(InvalidForecastRequestException) as exc_info:
            await forecast_use_case.get_forecast(
                district_id="INVALID_ID", metric="flow_rate", horizon=7
            )

        assert exc_info.value.field == "district_id"
        assert exc_info.value.value == "INVALID_ID"
        assert "Must match pattern DIST_XXX" in str(exc_info.value)

        # Verify repository not called
        mock_repository.get_model_forecast.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_forecast_invalid_metric(
        self, forecast_use_case, mock_repository
    ):
        """Test error handling for invalid metric."""
        # Act & Assert
        with pytest.raises(InvalidForecastRequestException) as exc_info:
            await forecast_use_case.get_forecast(
                district_id="DIST_001", metric="invalid_metric", horizon=7
            )

        assert exc_info.value.field == "metric"
        assert exc_info.value.value == "invalid_metric"
        assert "Must be one of" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_forecast_invalid_horizon(
        self, forecast_use_case, mock_repository
    ):
        """Test error handling for invalid horizon."""
        # Test horizon too low
        with pytest.raises(InvalidForecastRequestException) as exc_info:
            await forecast_use_case.get_forecast(
                district_id="DIST_001", metric="flow_rate", horizon=0
            )

        assert exc_info.value.field == "horizon"
        assert exc_info.value.value == 0

        # Test horizon too high
        with pytest.raises(InvalidForecastRequestException) as exc_info:
            await forecast_use_case.get_forecast(
                district_id="DIST_001", metric="flow_rate", horizon=8
            )

        assert exc_info.value.field == "horizon"
        assert exc_info.value.value == 8

    @pytest.mark.asyncio
    async def test_get_forecast_not_found(self, forecast_use_case, mock_repository):
        """Test handling of forecast not found error."""
        # Arrange
        mock_repository.get_model_forecast.side_effect = ForecastNotFoundException(
            district_id="DIST_001", metric="flow_rate", horizon=7
        )

        # Act & Assert
        with pytest.raises(ForecastNotFoundException):
            await forecast_use_case.get_forecast(
                district_id="DIST_001", metric="flow_rate", horizon=7
            )

    @pytest.mark.asyncio
    async def test_get_forecast_service_error(self, forecast_use_case, mock_repository):
        """Test handling of service errors."""
        # Arrange
        mock_repository.get_model_forecast.side_effect = ForecastServiceException(
            message="BigQuery error", service="bigquery"
        )

        # Act & Assert
        with pytest.raises(ForecastServiceException):
            await forecast_use_case.get_forecast(
                district_id="DIST_001", metric="flow_rate", horizon=7
            )

    @pytest.mark.asyncio
    async def test_get_forecast_missing_confidence_level(
        self, forecast_use_case, mock_repository
    ):
        """Test handling of missing confidence level in response."""
        # Arrange
        df_without_confidence = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-07-05", periods=3, freq="D", tz="UTC"),
                "forecast_value": [100.0, 101.0, 102.0],
                "lower_bound": [95.0, 96.0, 97.0],
                "upper_bound": [105.0, 106.0, 107.0],
            }
        )
        mock_repository.get_model_forecast.return_value = df_without_confidence

        # Act
        result = await forecast_use_case.get_forecast(
            district_id="DIST_001", metric="flow_rate", horizon=3
        )

        # Assert
        assert "confidence_level" in result.columns
        assert (result["confidence_level"] == 0.95).all()

    @pytest.mark.asyncio
    async def test_get_forecast_with_nulls(self, forecast_use_case, mock_repository):
        """Test error handling for null values in forecast data."""
        # Arrange
        df_with_nulls = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-07-05", periods=3, freq="D", tz="UTC"),
                "forecast_value": [100.0, None, 102.0],  # Null value
                "lower_bound": [95.0, 96.0, 97.0],
                "upper_bound": [105.0, 106.0, 107.0],
                "confidence_level": [0.95] * 3,
            }
        )
        mock_repository.get_model_forecast.return_value = df_with_nulls

        # Act & Assert
        with pytest.raises(ForecastServiceException) as exc_info:
            await forecast_use_case.get_forecast(
                district_id="DIST_001", metric="flow_rate", horizon=3
            )

        assert "null values" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_forecast_timezone_handling(
        self, forecast_use_case, mock_repository
    ):
        """Test proper timezone handling for timestamps."""
        # Arrange - DataFrame without timezone
        df_no_tz = pd.DataFrame(
            {
                "timestamp": pd.date_range("2025-07-05", periods=3, freq="D"),
                "forecast_value": [100.0, 101.0, 102.0],
                "lower_bound": [95.0, 96.0, 97.0],
                "upper_bound": [105.0, 106.0, 107.0],
                "confidence_level": [0.95] * 3,
            }
        )
        mock_repository.get_model_forecast.return_value = df_no_tz

        # Act
        result = await forecast_use_case.get_forecast(
            district_id="DIST_001", metric="flow_rate", horizon=3
        )

        # Assert
        assert result["timestamp"].dt.tz is not None
        assert str(result["timestamp"].dt.tz) == "UTC"

    @pytest.mark.asyncio
    async def test_get_forecast_all_metrics(
        self, forecast_use_case, mock_repository, sample_forecast_df
    ):
        """Test forecast retrieval for all valid metrics."""
        # Arrange
        metrics = ["flow_rate", "pressure", "reservoir_level"]
        mock_repository.get_model_forecast.return_value = sample_forecast_df

        # Act & Assert
        for metric in metrics:
            result = await forecast_use_case.get_forecast(
                district_id="DIST_001", metric=metric, horizon=7
            )

            assert isinstance(result, pd.DataFrame)
            assert (result["metric"] == metric).all()

    @pytest.mark.asyncio
    async def test_get_forecast_performance_tracking(
        self, forecast_use_case, mock_repository, sample_forecast_df, mock_metrics
    ):
        """Test that performance metrics are properly tracked."""
        # Arrange
        mock_repository.get_model_forecast.return_value = sample_forecast_df

        # Act
        await forecast_use_case.get_forecast(
            district_id="DIST_001", metric="flow_rate", horizon=7
        )

        # Assert
        mock_metrics.record_count.assert_called_once_with(
            "forecast_requests", {"district": "DIST_001", "metric": "flow_rate"}
        )
        mock_metrics.record_latency.assert_called_once()

        # Verify latency was recorded with proper operation name
        call_args = mock_metrics.record_latency.call_args
        assert call_args[0][0] == "forecast_retrieval"
        assert isinstance(call_args[0][1], float)
        assert call_args[0][1] > 0  # Positive latency

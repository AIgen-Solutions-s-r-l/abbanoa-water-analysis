"""
Unit tests for ForecastingService.

Tests all forecasting business logic including consumption prediction,
model training, and accuracy assessment.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from typing import Dict, Any, List

from src.api.services.forecasting_service import ForecastingService
from src.schemas.api.forecasting import (
    ConsumptionForecast, ModelTraining, AccuracyReport, 
    ForecastAnalysis, ModelComparison, ForecastAlert
)


@pytest.mark.unit
@pytest.mark.forecasting
class TestForecastingService:
    """Test suite for ForecastingService."""

    @pytest.fixture
    def forecasting_service(self):
        """Provide ForecastingService instance."""
        return ForecastingService()

    @pytest.fixture
    def mock_hybrid_service(self):
        """Provide mocked HybridDataService."""
        mock = AsyncMock()
        mock.get_consumption_data.return_value = [
            {
                "node_id": "NODE_001",
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "consumption_value": 100.0 + i * 5,
                "region": "North"
            }
            for i in range(30)
        ]
        return mock

    @pytest.mark.asyncio
    async def test_generate_consumption_forecast_success(
        self, forecasting_service, mock_hybrid_service, test_date_range
    ):
        """Test successful consumption forecast generation."""
        result = await forecasting_service.generate_consumption_forecast(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"],
            forecast_horizon=7
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(item, ConsumptionForecast) for item in result)

    @pytest.mark.asyncio
    async def test_train_forecasting_model_success(
        self, forecasting_service, mock_hybrid_service, test_date_range
    ):
        """Test successful model training."""
        result = await forecasting_service.train_forecasting_model(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"],
            model_type="arima"
        )

        assert isinstance(result, ModelTraining)
        assert hasattr(result, 'model_id')
        assert hasattr(result, 'training_accuracy')
        assert hasattr(result, 'validation_accuracy')

    @pytest.mark.asyncio
    async def test_evaluate_model_accuracy_success(
        self, forecasting_service, mock_hybrid_service, test_date_range
    ):
        """Test successful model accuracy evaluation."""
        result = await forecasting_service.evaluate_model_accuracy(
            mock_hybrid_service,
            "MODEL_001",
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, AccuracyReport)
        assert hasattr(result, 'accuracy_metrics')
        assert hasattr(result, 'error_statistics')

    def test_model_selection_logic(self, forecasting_service):
        """Test model selection based on data characteristics."""
        # Test with short time series
        short_data = [{"value": 100 + i} for i in range(10)]
        short_model = forecasting_service._select_optimal_model(short_data)
        assert short_model in ["linear_regression", "arima", "lstm", "prophet"]

        # Test with long time series
        long_data = [{"value": 100 + i} for i in range(1000)]
        long_model = forecasting_service._select_optimal_model(long_data)
        assert long_model in ["linear_regression", "arima", "lstm", "prophet"]

    def test_forecast_accuracy_calculation(self, forecasting_service):
        """Test forecast accuracy calculation methods."""
        actual = [100, 110, 120, 130, 140]
        predicted = [105, 115, 118, 132, 138]

        # Test MAPE calculation
        mape = forecasting_service._calculate_mape(actual, predicted)
        assert isinstance(mape, float)
        assert 0 <= mape <= 100

        # Test RMSE calculation  
        rmse = forecasting_service._calculate_rmse(actual, predicted)
        assert isinstance(rmse, float)
        assert rmse >= 0

    def test_seasonal_pattern_detection(self, forecasting_service):
        """Test seasonal pattern detection."""
        # Create data with daily seasonality
        seasonal_data = [
            {
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "value": 100 + 50 * abs((i % 24 - 12) / 12)  # Peak at noon
            }
            for i in range(168)  # 1 week of hourly data
        ]

        patterns = forecasting_service._detect_seasonal_patterns(seasonal_data)
        assert "daily" in patterns or "weekly" in patterns

    def test_trend_analysis(self, forecasting_service):
        """Test trend analysis in time series."""
        # Increasing trend
        increasing_data = [{"value": 100 + i * 2} for i in range(50)]
        trend = forecasting_service._analyze_trend(increasing_data)
        assert trend["direction"] == "increasing"

        # Decreasing trend
        decreasing_data = [{"value": 200 - i * 2} for i in range(50)]
        trend = forecasting_service._analyze_trend(decreasing_data)
        assert trend["direction"] == "decreasing"

    @pytest.mark.parametrize("model_type", ["arima", "lstm", "prophet", "linear_regression"])
    def test_model_specific_training(self, forecasting_service, model_type):
        """Test training for different model types."""
        sample_data = [
            {
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "value": 100 + i * 2
            }
            for i in range(100)
        ]

        model_params = forecasting_service._train_model(sample_data, model_type)
        assert isinstance(model_params, dict)
        assert "model_type" in model_params
        assert model_params["model_type"] == model_type

    def test_confidence_interval_calculation(self, forecasting_service):
        """Test confidence interval calculation."""
        predictions = [100, 110, 120, 130, 140]
        errors = [5, 8, 3, 6, 4]

        intervals = forecasting_service._calculate_confidence_intervals(predictions, errors)
        assert len(intervals) == len(predictions)
        for interval in intervals:
            assert len(interval) == 2  # Lower and upper bounds
            assert interval[0] <= interval[1]  # Lower <= Upper

    def test_forecast_validation(self, forecasting_service):
        """Test forecast validation logic."""
        # Valid forecast
        valid_forecast = {
            "node_id": "NODE_001",
            "predicted_value": 150.0,
            "confidence_interval": [140.0, 160.0],
            "forecast_date": datetime.now().isoformat()
        }
        assert forecasting_service._validate_forecast(valid_forecast) is True

        # Invalid forecast - negative prediction
        invalid_forecast = valid_forecast.copy()
        invalid_forecast["predicted_value"] = -50.0
        assert forecasting_service._validate_forecast(invalid_forecast) is False 
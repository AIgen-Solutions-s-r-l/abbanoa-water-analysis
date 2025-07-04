"""
Integration tests for BigQueryForecastRepository.

Tests the integration between the forecast repository and BigQuery,
using a test dataset and mock ML models.
"""

import asyncio
import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest
from google.cloud import bigquery

from src.infrastructure.clients.async_bigquery_client import AsyncBigQueryClient
from src.infrastructure.repositories.bigquery_forecast_repository import (
    BigQueryForecastRepository,
)
from src.shared.exceptions.forecast_exceptions import (
    ForecastNotFoundException,
    ForecastServiceException,
)


@pytest.fixture
async def async_bigquery_client():
    """Create async BigQuery client for testing."""
    # Use test project or mock if not available
    project_id = os.getenv("TEST_GCP_PROJECT", "test-project")
    dataset_id = os.getenv("TEST_DATASET", "test_dataset")
    
    client = AsyncBigQueryClient(
        project_id=project_id,
        dataset_id=dataset_id,
        location="EU",
        query_timeout_ms=200,
        enable_cache=False  # Disable cache for tests
    )
    
    await client.initialize()
    yield client
    await client.close()


@pytest.fixture
def mock_bigquery_response():
    """Create mock BigQuery response data."""
    data = {
        'timestamp': pd.date_range(
            start='2025-07-05 00:00:00',
            periods=7,
            freq='D',
            tz='UTC'
        ),
        'forecast_value': [100.5, 102.3, 101.8, 103.2, 104.1, 102.9, 101.7],
        'lower_bound': [95.0, 96.5, 95.8, 97.1, 97.9, 96.7, 95.5],
        'upper_bound': [106.0, 108.1, 107.8, 109.3, 110.3, 109.1, 107.9],
        'confidence_level': [0.95] * 7
    }
    return pd.DataFrame(data)


@pytest.mark.integration
class TestBigQueryForecastRepository:
    """Integration test suite for BigQueryForecastRepository."""
    
    @pytest.mark.asyncio
    async def test_get_model_forecast_success(
        self,
        async_bigquery_client,
        mock_bigquery_response
    ):
        """Test successful forecast retrieval from BigQuery."""
        # Mock the execute_query method
        async_bigquery_client.execute_query = AsyncMock(
            return_value=mock_bigquery_response
        )
        
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        # Mock model existence check
        repo.check_model_exists = AsyncMock(return_value=True)
        
        # Act
        result = await repo.get_model_forecast(
            model_name="arima_dist001_flow_rate",
            district_metric_id="DIST_001_flow_rate",
            horizon=7
        )
        
        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 7
        assert list(result.columns) == [
            'timestamp', 'forecast_value', 'lower_bound',
            'upper_bound', 'confidence_level'
        ]
        assert result['timestamp'].dt.tz is not None
        
        # Verify query execution
        async_bigquery_client.execute_query.assert_called_once()
        call_args = async_bigquery_client.execute_query.call_args
        assert "ML.FORECAST" in call_args[1]['query']
        assert call_args[1]['timeout_ms'] == 200
    
    @pytest.mark.asyncio
    async def test_get_model_forecast_model_not_found(
        self,
        async_bigquery_client
    ):
        """Test error when model doesn't exist."""
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        # Mock model existence check to return False
        repo.check_model_exists = AsyncMock(return_value=False)
        
        # Act & Assert
        with pytest.raises(ForecastNotFoundException) as exc_info:
            await repo.get_model_forecast(
                model_name="arima_dist999_flow_rate",
                district_metric_id="DIST_999_flow_rate",
                horizon=7
            )
        
        assert exc_info.value.district_id == "DIST_999"
        assert exc_info.value.metric == "flow_rate"
        assert exc_info.value.horizon == 7
    
    @pytest.mark.asyncio
    async def test_get_model_forecast_empty_result(
        self,
        async_bigquery_client
    ):
        """Test error when forecast query returns empty result."""
        # Mock empty response
        async_bigquery_client.execute_query = AsyncMock(
            return_value=pd.DataFrame()
        )
        
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        # Mock model existence check
        repo.check_model_exists = AsyncMock(return_value=True)
        
        # Act & Assert
        with pytest.raises(ForecastNotFoundException) as exc_info:
            await repo.get_model_forecast(
                model_name="arima_dist001_flow_rate",
                district_metric_id="DIST_001_flow_rate",
                horizon=7
            )
        
        assert "No forecast data returned" in str(exc_info.value.details)
    
    @pytest.mark.asyncio
    async def test_check_model_exists_true(
        self,
        async_bigquery_client
    ):
        """Test model existence check when model exists."""
        # Mock response with one row
        async_bigquery_client.execute_query = AsyncMock(
            return_value=pd.DataFrame({'exists': [1]})
        )
        
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        # Act
        exists = await repo.check_model_exists("arima_dist001_flow_rate")
        
        # Assert
        assert exists is True
        
        # Verify query
        call_args = async_bigquery_client.execute_query.call_args
        assert "INFORMATION_SCHEMA.MODELS" in call_args[1]['query']
        assert call_args[1]['timeout_ms'] == 100
        assert call_args[1]['use_cache'] is True
    
    @pytest.mark.asyncio
    async def test_check_model_exists_false(
        self,
        async_bigquery_client
    ):
        """Test model existence check when model doesn't exist."""
        # Mock empty response
        async_bigquery_client.execute_query = AsyncMock(
            return_value=pd.DataFrame()
        )
        
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        # Act
        exists = await repo.check_model_exists("nonexistent_model")
        
        # Assert
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_check_model_exists_error_handling(
        self,
        async_bigquery_client
    ):
        """Test model existence check handles errors gracefully."""
        # Mock query error
        async_bigquery_client.execute_query = AsyncMock(
            side_effect=Exception("BigQuery error")
        )
        
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        # Act
        exists = await repo.check_model_exists("arima_dist001_flow_rate")
        
        # Assert - Should return False on error
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_get_model_metadata_success(
        self,
        async_bigquery_client
    ):
        """Test successful model metadata retrieval."""
        # Mock metadata response
        metadata_df = pd.DataFrame([{
            'model_name': 'arima_dist001_flow_rate',
            'model_type': 'ARIMA_PLUS',
            'created_at': datetime.now(timezone.utc),
            'last_updated': datetime.now(timezone.utc),
            'training_options': {'horizon': 7}
        }])
        
        # Mock performance response
        perf_df = pd.DataFrame([{
            'mape': 0.134,
            'mae': 13.4,
            'rmse': 18.9
        }])
        
        # Set up mock responses
        async_bigquery_client.execute_query = AsyncMock(
            side_effect=[metadata_df, perf_df]
        )
        
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        # Act
        metadata = await repo.get_model_metadata("arima_dist001_flow_rate")
        
        # Assert
        assert metadata['model_name'] == 'arima_dist001_flow_rate'
        assert metadata['model_type'] == 'ARIMA_PLUS'
        assert 'performance_metrics' in metadata
        assert metadata['performance_metrics']['mape'] == 0.134
    
    @pytest.mark.asyncio
    async def test_get_model_metadata_not_found(
        self,
        async_bigquery_client
    ):
        """Test error when model metadata not found."""
        # Mock empty response
        async_bigquery_client.execute_query = AsyncMock(
            return_value=pd.DataFrame()
        )
        
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        # Act & Assert
        with pytest.raises(ForecastNotFoundException):
            await repo.get_model_metadata("nonexistent_model")
    
    @pytest.mark.asyncio
    async def test_timezone_handling(
        self,
        async_bigquery_client
    ):
        """Test proper timezone handling for forecast timestamps."""
        # Create response without timezone
        data = {
            'timestamp': pd.date_range('2025-07-05', periods=3, freq='D'),
            'forecast_value': [100.0, 101.0, 102.0],
            'lower_bound': [95.0, 96.0, 97.0],
            'upper_bound': [105.0, 106.0, 107.0],
            'confidence_level': [0.95] * 3
        }
        df_no_tz = pd.DataFrame(data)
        
        async_bigquery_client.execute_query = AsyncMock(
            return_value=df_no_tz
        )
        
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        repo.check_model_exists = AsyncMock(return_value=True)
        
        # Act
        result = await repo.get_model_forecast(
            model_name="arima_dist001_flow_rate",
            district_metric_id="DIST_001_flow_rate",
            horizon=3
        )
        
        # Assert
        assert result['timestamp'].dt.tz is not None
        assert str(result['timestamp'].dt.tz) == 'UTC'
    
    @pytest.mark.asyncio
    async def test_missing_confidence_level_handling(
        self,
        async_bigquery_client
    ):
        """Test handling of missing confidence level column."""
        # Create response without confidence_level
        data = {
            'timestamp': pd.date_range('2025-07-05', periods=3, freq='D', tz='UTC'),
            'forecast_value': [100.0, 101.0, 102.0],
            'lower_bound': [95.0, 96.0, 97.0],
            'upper_bound': [105.0, 106.0, 107.0]
        }
        df_no_confidence = pd.DataFrame(data)
        
        async_bigquery_client.execute_query = AsyncMock(
            return_value=df_no_confidence
        )
        
        # Create repository
        repo = BigQueryForecastRepository(
            client=async_bigquery_client,
            ml_dataset_id="ml_models"
        )
        
        repo.check_model_exists = AsyncMock(return_value=True)
        
        # Act
        result = await repo.get_model_forecast(
            model_name="arima_dist001_flow_rate",
            district_metric_id="DIST_001_flow_rate",
            horizon=3
        )
        
        # Assert
        assert 'confidence_level' in result.columns
        assert (result['confidence_level'] == 0.95).all()
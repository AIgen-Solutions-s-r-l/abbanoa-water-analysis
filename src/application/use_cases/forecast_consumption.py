"""
Forecast consumption use case implementation.

This module implements the core business logic for retrieving and processing
forecast data, following clean architecture principles.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from src.application.interfaces.forecast_repository import ForecastRepositoryInterface
from src.domain.value_objects.forecast_request import ForecastRequest
from src.domain.value_objects.forecast_response import ForecastResponse
from src.shared.exceptions.forecast_exceptions import (
    ForecastServiceException,
    InvalidForecastRequestException,
)


class MetricsCollector:
    """Simple metrics collector for performance tracking."""
    
    def __init__(self):
        self.metrics = {}
    
    def record_latency(self, operation: str, latency_ms: float) -> None:
        """Record operation latency."""
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(latency_ms)
    
    def record_count(self, metric_name: str, tags: dict) -> None:
        """Record count metric with tags."""
        key = f"{metric_name}:{tags}"
        self.metrics[key] = self.metrics.get(key, 0) + 1


class ForecastConsumption:
    """
    Use case for consuming forecast data.
    
    Implements the business logic for retrieving forecast data from ML models,
    with proper validation, error handling, and performance tracking.
    """
    
    def __init__(
        self,
        forecast_repository: ForecastRepositoryInterface,
        logger: Optional[logging.Logger] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        """
        Initialize forecast consumption use case.
        
        Args:
            forecast_repository: Repository for forecast data access
            logger: Logger instance
            metrics: Metrics collector for monitoring
        """
        self._repository = forecast_repository
        self._logger = logger or logging.getLogger(__name__)
        self._metrics = metrics or MetricsCollector()
    
    async def get_forecast(
        self,
        district_id: str,
        metric: str,
        horizon: int
    ) -> pd.DataFrame:
        """
        Retrieve forecast data for a specific district and metric.
        
        Args:
            district_id: District identifier (e.g., 'DIST_001')
            metric: Metric type ('flow_rate', 'reservoir_level', 'pressure')
            horizon: Forecast horizon in days (1-7)
        
        Returns:
            pd.DataFrame: Forecast data with columns:
                - timestamp: Forecast timestamp (UTC)
                - district_id: District identifier
                - metric: Metric type
                - forecast_value: Predicted value
                - lower_bound: Prediction interval lower bound
                - upper_bound: Prediction interval upper bound
                - confidence_level: Confidence level (default 0.95)
        
        Raises:
            InvalidForecastRequestException: Invalid input parameters
            ForecastNotFoundException: No forecast available
            ForecastServiceException: Service error
            ForecastTimeoutException: Request timeout
        """
        start_time = time.time()
        request_id = f"{district_id}_{metric}_{horizon}_{int(start_time)}"
        
        self._logger.info(
            f"Processing forecast request: {request_id} - "
            f"district={district_id}, metric={metric}, horizon={horizon}"
        )
        
        try:
            # Validate and create request object
            try:
                forecast_request = ForecastRequest(
                    district_id=district_id,
                    metric=metric,
                    horizon=horizon
                )
            except ValueError as e:
                self._logger.warning(f"Invalid forecast request: {str(e)}")
                
                # Determine which field is invalid
                field = "unknown"
                value = None
                if "district_id" in str(e):
                    field = "district_id"
                    value = district_id
                elif "metric" in str(e):
                    field = "metric"
                    value = metric
                elif "horizon" in str(e):
                    field = "horizon"
                    value = horizon
                
                raise InvalidForecastRequestException(
                    message=str(e),
                    field=field,
                    value=value
                )
            
            # Record request metrics
            self._metrics.record_count(
                "forecast_requests",
                {"district": district_id, "metric": metric}
            )
            
            # Retrieve forecast from repository
            model_forecast_df = await self._repository.get_model_forecast(
                model_name=forecast_request.model_name,
                district_metric_id=forecast_request.district_metric_id,
                horizon=forecast_request.horizon
            )
            
            # Process and format the response
            result_df = self._format_forecast_dataframe(
                df=model_forecast_df,
                district_id=district_id,
                metric=metric
            )
            
            # Create response object for validation
            forecast_response = ForecastResponse.from_dataframe(
                df=result_df,
                district_id=district_id,
                metric=metric,
                generated_at=datetime.now(timezone.utc)
            )
            
            # Record success metrics
            elapsed_ms = (time.time() - start_time) * 1000
            self._metrics.record_latency("forecast_retrieval", elapsed_ms)
            
            self._logger.info(
                f"Forecast request {request_id} completed successfully "
                f"in {elapsed_ms:.2f}ms"
            )
            
            # Return the formatted DataFrame
            return result_df
            
        except (InvalidForecastRequestException, ForecastServiceException):
            # Re-raise domain exceptions
            raise
            
        except Exception as e:
            # Wrap unexpected errors
            self._logger.error(
                f"Unexpected error processing forecast request {request_id}: {str(e)}"
            )
            raise ForecastServiceException(
                message=f"Failed to process forecast request: {str(e)}",
                service="forecast_consumption",
                original_error=e
            )
    
    def _format_forecast_dataframe(
        self,
        df: pd.DataFrame,
        district_id: str,
        metric: str
    ) -> pd.DataFrame:
        """
        Format forecast DataFrame to match expected output format.
        
        Args:
            df: Raw forecast DataFrame from repository
            district_id: District identifier
            metric: Metric type
        
        Returns:
            Formatted DataFrame with all required columns
        """
        # Create a copy to avoid modifying original
        result_df = df.copy()
        
        # Add district and metric columns
        result_df['district_id'] = district_id
        result_df['metric'] = metric
        
        # Ensure all required columns are present
        required_columns = [
            'timestamp', 'district_id', 'metric', 'forecast_value',
            'lower_bound', 'upper_bound', 'confidence_level'
        ]
        
        for col in required_columns:
            if col not in result_df.columns:
                if col == 'confidence_level':
                    result_df[col] = 0.95
                else:
                    raise ForecastServiceException(
                        f"Missing required column '{col}' in forecast data",
                        service="forecast_formatting"
                    )
        
        # Select and order columns
        result_df = result_df[required_columns]
        
        # Ensure timestamp is UTC timezone aware
        if result_df['timestamp'].dt.tz is None:
            result_df['timestamp'] = result_df['timestamp'].dt.tz_localize('UTC')
        
        # Sort by timestamp
        result_df = result_df.sort_values('timestamp')
        
        # Reset index
        result_df = result_df.reset_index(drop=True)
        
        # Validate no missing values
        if result_df.isnull().any().any():
            null_columns = result_df.columns[result_df.isnull().any()].tolist()
            raise ForecastServiceException(
                f"Forecast data contains null values in columns: {null_columns}",
                service="forecast_formatting"
            )
        
        return result_df
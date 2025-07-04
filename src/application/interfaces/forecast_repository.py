"""
Forecast repository interface following clean architecture principles.

This module defines the abstract interface for forecast data access,
allowing the application layer to remain independent of infrastructure details.
"""

from abc import ABC, abstractmethod
from typing import Protocol

import pandas as pd


class ForecastRepositoryInterface(ABC):
    """
    Abstract interface for forecast data repository.
    
    Defines the contract for retrieving forecast data from ML models,
    independent of the underlying storage mechanism (BigQuery, etc.).
    """
    
    @abstractmethod
    async def get_model_forecast(
        self,
        model_name: str,
        district_metric_id: str,
        horizon: int
    ) -> pd.DataFrame:
        """
        Retrieve forecast data from a specific ML model.
        
        Args:
            model_name: Name of the ML model (e.g., 'arima_dist001_flow_rate')
            district_metric_id: Combined district and metric ID (e.g., 'DIST_001_flow_rate')
            horizon: Forecast horizon in days (1-7)
        
        Returns:
            DataFrame with columns:
                - timestamp: Forecast timestamp (UTC)
                - forecast_value: Predicted value
                - lower_bound: Prediction interval lower bound
                - upper_bound: Prediction interval upper bound
                - confidence_level: Confidence level
        
        Raises:
            ForecastNotFoundException: Model or forecast not found
            ForecastServiceException: Service-level error
            ForecastTimeoutException: Request timeout
        """
        pass
    
    @abstractmethod
    async def check_model_exists(self, model_name: str) -> bool:
        """
        Check if a specific ML model exists.
        
        Args:
            model_name: Name of the ML model
        
        Returns:
            True if model exists, False otherwise
        
        Raises:
            ForecastServiceException: Service-level error
        """
        pass
    
    @abstractmethod
    async def get_model_metadata(self, model_name: str) -> dict:
        """
        Retrieve metadata about a specific ML model.
        
        Args:
            model_name: Name of the ML model
        
        Returns:
            Dictionary containing model metadata:
                - created_at: Model creation timestamp
                - last_updated: Last training timestamp
                - model_type: Type of model (e.g., 'ARIMA_PLUS')
                - performance_metrics: Latest performance metrics
        
        Raises:
            ForecastNotFoundException: Model not found
            ForecastServiceException: Service-level error
        """
        pass


class ForecastRepositoryProtocol(Protocol):
    """
    Protocol definition for forecast repository.
    
    Provides a more flexible interface definition using Protocol,
    allowing structural typing without explicit inheritance.
    """
    
    async def get_model_forecast(
        self,
        model_name: str,
        district_metric_id: str,
        horizon: int
    ) -> pd.DataFrame:
        """Get forecast from model."""
        ...
    
    async def check_model_exists(self, model_name: str) -> bool:
        """Check if model exists."""
        ...
    
    async def get_model_metadata(self, model_name: str) -> dict:
        """Get model metadata."""
        ...
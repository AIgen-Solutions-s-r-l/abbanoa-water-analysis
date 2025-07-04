"""
Forecast response value object for encapsulating forecast results.

This module defines the ForecastResponse value object that represents
the forecast data returned from ML models in a domain-friendly format.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

import pandas as pd


@dataclass(frozen=True)
class ForecastPoint:
    """
    A single point in a forecast time series.
    
    Attributes:
        timestamp: Forecast timestamp (UTC)
        forecast_value: Predicted value
        lower_bound: Prediction interval lower bound
        upper_bound: Prediction interval upper bound
        confidence_level: Confidence level (default 0.95)
    """
    
    timestamp: datetime
    forecast_value: float
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.95
    
    def __post_init__(self) -> None:
        """Validate forecast point data."""
        if self.lower_bound > self.forecast_value:
            raise ValueError(
                f"Lower bound ({self.lower_bound}) cannot be greater than "
                f"forecast value ({self.forecast_value})"
            )
        
        if self.upper_bound < self.forecast_value:
            raise ValueError(
                f"Upper bound ({self.upper_bound}) cannot be less than "
                f"forecast value ({self.forecast_value})"
            )
        
        if not (0 < self.confidence_level <= 1):
            raise ValueError(
                f"Confidence level ({self.confidence_level}) must be between 0 and 1"
            )


@dataclass(frozen=True)
class ForecastResponse:
    """
    Value object representing a complete forecast response.
    
    Encapsulates the forecast data with metadata about the request
    that generated it.
    
    Attributes:
        district_id: District identifier
        metric: Metric type
        forecast_points: List of forecast points
        generated_at: When the forecast was generated
        model_version: Version of the model used (optional)
    """
    
    district_id: str
    metric: str
    forecast_points: List[ForecastPoint]
    generated_at: datetime
    model_version: str | None = None
    
    def __post_init__(self) -> None:
        """Validate forecast response data."""
        if not self.forecast_points:
            raise ValueError("Forecast response must contain at least one point")
        
        # Ensure points are sorted by timestamp
        sorted_points = sorted(self.forecast_points, key=lambda p: p.timestamp)
        if sorted_points != self.forecast_points:
            # Use object.__setattr__ to modify frozen dataclass
            object.__setattr__(self, 'forecast_points', sorted_points)
    
    @property
    def horizon(self) -> int:
        """Get the forecast horizon in days."""
        if not self.forecast_points:
            return 0
        
        first_timestamp = self.forecast_points[0].timestamp
        last_timestamp = self.forecast_points[-1].timestamp
        return (last_timestamp.date() - first_timestamp.date()).days + 1
    
    @property
    def start_date(self) -> datetime:
        """Get the first forecast timestamp."""
        return self.forecast_points[0].timestamp if self.forecast_points else None
    
    @property
    def end_date(self) -> datetime:
        """Get the last forecast timestamp."""
        return self.forecast_points[-1].timestamp if self.forecast_points else None
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert forecast response to pandas DataFrame.
        
        Returns:
            DataFrame with columns: timestamp, district_id, metric,
            forecast_value, lower_bound, upper_bound, confidence_level
        """
        data = []
        for point in self.forecast_points:
            data.append({
                'timestamp': point.timestamp,
                'district_id': self.district_id,
                'metric': self.metric,
                'forecast_value': point.forecast_value,
                'lower_bound': point.lower_bound,
                'upper_bound': point.upper_bound,
                'confidence_level': point.confidence_level
            })
        
        df = pd.DataFrame(data)
        
        # Ensure timestamp is timezone-aware UTC
        if not df.empty and df['timestamp'].dt.tz is None:
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
        
        return df
    
    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        district_id: str,
        metric: str,
        generated_at: datetime | None = None
    ) -> ForecastResponse:
        """
        Create ForecastResponse from a DataFrame.
        
        Args:
            df: DataFrame with forecast data
            district_id: District identifier
            metric: Metric type
            generated_at: When forecast was generated (defaults to now)
        
        Returns:
            ForecastResponse instance
        """
        if generated_at is None:
            generated_at = datetime.utcnow()
        
        forecast_points = []
        for _, row in df.iterrows():
            point = ForecastPoint(
                timestamp=row['timestamp'],
                forecast_value=row['forecast_value'],
                lower_bound=row['lower_bound'],
                upper_bound=row['upper_bound'],
                confidence_level=row.get('confidence_level', 0.95)
            )
            forecast_points.append(point)
        
        return cls(
            district_id=district_id,
            metric=metric,
            forecast_points=forecast_points,
            generated_at=generated_at
        )
"""
Forecast request value object for encapsulating forecast query parameters.

This module defines the ForecastRequest value object following DDD principles,
ensuring immutability and validation of forecast request parameters.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, Pattern

from src.domain.exceptions import ValidationError


@dataclass(frozen=True)
class ForecastRequest:
    """
    Value object representing a forecast request.
    
    Encapsulates and validates the parameters needed to request a forecast
    from the ML models. Ensures all parameters meet business rules.
    
    Attributes:
        district_id: District identifier (e.g., 'DIST_001')
        metric: Metric type ('flow_rate', 'reservoir_level', 'pressure')
        horizon: Forecast horizon in days (1-7)
    """
    
    district_id: str
    metric: str
    horizon: int
    
    # Class-level constants
    VALID_METRICS: ClassVar[set[str]] = {'flow_rate', 'reservoir_level', 'pressure'}
    DISTRICT_PATTERN: ClassVar[Pattern[str]] = re.compile(r'^DIST_\d{3}$')
    MIN_HORIZON: ClassVar[int] = 1
    MAX_HORIZON: ClassVar[int] = 7
    
    def __post_init__(self) -> None:
        """Validate forecast request parameters after initialization."""
        self._validate_district_id()
        self._validate_metric()
        self._validate_horizon()
    
    def _validate_district_id(self) -> None:
        """Validate district ID format."""
        if not self.DISTRICT_PATTERN.match(self.district_id):
            raise ValidationError(
                "district_id",
                f"Invalid district_id '{self.district_id}'. "
                f"Must match pattern DIST_XXX where XXX is a 3-digit number."
            )
    
    def _validate_metric(self) -> None:
        """Validate metric is in allowed set."""
        if self.metric not in self.VALID_METRICS:
            raise ValidationError(
                "metric",
                f"Invalid metric '{self.metric}'. "
                f"Must be one of: {', '.join(sorted(self.VALID_METRICS))}"
            )
    
    def _validate_horizon(self) -> None:
        """Validate horizon is within allowed range."""
        if not (self.MIN_HORIZON <= self.horizon <= self.MAX_HORIZON):
            raise ValidationError(
                "horizon",
                f"Invalid horizon {self.horizon}. "
                f"Must be between {self.MIN_HORIZON} and {self.MAX_HORIZON} days."
            )
    
    @property
    def model_name(self) -> str:
        """
        Generate the BigQuery ML model name for this request.
        
        Returns:
            Model name in format: arima_{district_lower}_{metric}
        """
        return f"arima_{self.district_id.lower()}_{self.metric}"
    
    @property
    def district_metric_id(self) -> str:
        """
        Generate the district-metric identifier.
        
        Returns:
            Combined identifier in format: {district_id}_{metric}
        """
        return f"{self.district_id}_{self.metric}"
    
    def __str__(self) -> str:
        """String representation of the forecast request."""
        return (
            f"ForecastRequest(district={self.district_id}, "
            f"metric={self.metric}, horizon={self.horizon})"
        )
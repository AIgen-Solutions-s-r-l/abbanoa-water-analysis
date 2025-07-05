"""
Forecast-specific exceptions for error handling.

This module defines custom exceptions for the forecast use case,
providing clear error semantics and appropriate HTTP status code mappings.
"""

from typing import Optional


class ForecastException(Exception):
    """Base exception for all forecast-related errors."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ForecastNotFoundException(ForecastException):
    """
    Raised when a forecast cannot be found for the requested parameters.

    Maps to HTTP 404 Not Found.
    """

    def __init__(
        self,
        district_id: str,
        metric: str,
        horizon: int,
        details: Optional[dict] = None,
    ) -> None:
        message = (
            f"Forecast not found for district '{district_id}', "
            f"metric '{metric}', horizon {horizon} days"
        )
        super().__init__(message, details)
        self.district_id = district_id
        self.metric = metric
        self.horizon = horizon


class InvalidForecastRequestException(ForecastException):
    """
    Raised when forecast request parameters are invalid.

    Maps to HTTP 400 Bad Request.
    """

    def __init__(self, message: str, field: str, value: any) -> None:
        details = {"field": field, "value": value, "error": "validation_error"}
        super().__init__(message, details)
        self.field = field
        self.value = value


class ForecastServiceException(ForecastException):
    """
    Raised when there's a service-level error (BigQuery, model errors).

    Maps to HTTP 503 Service Unavailable.
    """

    def __init__(
        self, message: str, service: str, original_error: Optional[Exception] = None
    ) -> None:
        details = {
            "service": service,
            "error_type": (
                type(original_error).__name__ if original_error else "unknown"
            ),
        }
        super().__init__(message, details)
        self.service = service
        self.original_error = original_error


class ForecastTimeoutException(ForecastException):
    """
    Raised when a forecast request exceeds the timeout threshold.

    Maps to HTTP 504 Gateway Timeout.
    """

    def __init__(self, message: str, timeout_ms: int, operation: str) -> None:
        details = {"timeout_ms": timeout_ms, "operation": operation, "error": "timeout"}
        super().__init__(message, details)
        self.timeout_ms = timeout_ms
        self.operation = operation

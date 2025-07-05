"""Domain exceptions module."""

from .domain_exceptions import (
    BusinessRuleViolationException,
    DataQualityException,
    DomainException,
    EntityNotFoundException,
    InvalidMeasurementException,
    NetworkIntegrityException,
)

# Add ValidationError as an alias for BusinessRuleViolationException
ValidationError = BusinessRuleViolationException

__all__ = [
    "DomainException",
    "EntityNotFoundException",
    "InvalidMeasurementException",
    "BusinessRuleViolationException",
    "ValidationError",
    "DataQualityException",
    "NetworkIntegrityException",
]

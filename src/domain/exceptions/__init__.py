"""Domain exceptions module."""

from .domain_exceptions import (
    DomainException,
    EntityNotFoundException,
    InvalidMeasurementException,
    BusinessRuleViolationException,
    DataQualityException,
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
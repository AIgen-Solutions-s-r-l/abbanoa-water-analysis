"""Domain exceptions for water infrastructure monitoring system."""

from typing import Optional
from uuid import UUID


class DomainException(Exception):
    """Base exception for all domain-related errors."""
    
    def __init__(self, message: str, code: Optional[str] = None) -> None:
        super().__init__(message)
        self.code = code or self.__class__.__name__


class EntityNotFoundException(DomainException):
    """Exception raised when an entity is not found."""
    
    def __init__(self, entity_type: str, entity_id: UUID) -> None:
        message = f"{entity_type} with ID {entity_id} not found"
        super().__init__(message, "ENTITY_NOT_FOUND")
        self.entity_type = entity_type
        self.entity_id = entity_id


class InvalidMeasurementException(DomainException):
    """Exception raised when a measurement value is invalid."""
    
    def __init__(self, measurement_type: str, value: float, reason: str) -> None:
        message = f"Invalid {measurement_type} value {value}: {reason}"
        super().__init__(message, "INVALID_MEASUREMENT")
        self.measurement_type = measurement_type
        self.value = value
        self.reason = reason


class BusinessRuleViolationException(DomainException):
    """Exception raised when a business rule is violated."""
    
    def __init__(self, rule: str, message: str) -> None:
        super().__init__(message, "BUSINESS_RULE_VIOLATION")
        self.rule = rule


class DataQualityException(DomainException):
    """Exception raised when data quality issues are detected."""
    
    def __init__(self, node_id: UUID, quality_score: float, threshold: float) -> None:
        message = f"Data quality score {quality_score} below threshold {threshold} for node {node_id}"
        super().__init__(message, "DATA_QUALITY_ISSUE")
        self.node_id = node_id
        self.quality_score = quality_score
        self.threshold = threshold


class NetworkIntegrityException(DomainException):
    """Exception raised when network integrity is compromised."""
    
    def __init__(self, message: str, network_id: Optional[UUID] = None) -> None:
        super().__init__(message, "NETWORK_INTEGRITY_ERROR")
        self.network_id = network_id
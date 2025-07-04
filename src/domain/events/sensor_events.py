from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID

from src.domain.events.base import DomainEvent
from src.domain.value_objects.measurements import FlowRate, Pressure, Temperature


@dataclass
class AnomalyDetectedEvent(DomainEvent):
    """Event raised when an anomaly is detected in sensor readings."""

    node_id: UUID
    sensor_type: str
    anomaly_type: str
    severity: str
    measurement_value: float
    threshold: float
    description: str

    @property
    def event_type(self) -> str:
        return "anomaly_detected"

    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "node_id": str(self.node_id),
            "sensor_type": self.sensor_type,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "measurement_value": self.measurement_value,
            "threshold": self.threshold,
            "description": self.description,
        }


@dataclass
class ThresholdExceededEvent(DomainEvent):
    """Event raised when a measurement exceeds configured threshold."""

    node_id: UUID
    measurement_type: str
    current_value: float
    threshold_value: float
    threshold_type: str  # "upper" or "lower"

    @property
    def event_type(self) -> str:
        return "threshold_exceeded"

    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "node_id": str(self.node_id),
            "measurement_type": self.measurement_type,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "threshold_type": self.threshold_type,
        }


@dataclass
class SensorReadingAddedEvent(DomainEvent):
    """Event raised when a new sensor reading is added."""

    node_id: UUID
    reading_id: UUID
    timestamp: str
    measurements: Dict[str, float]

    @property
    def event_type(self) -> str:
        return "sensor_reading_added"

    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "node_id": str(self.node_id),
            "reading_id": str(self.reading_id),
            "timestamp": self.timestamp,
            "measurements": self.measurements,
        }


@dataclass
class DataQualityIssueEvent(DomainEvent):
    """Event raised when data quality issues are detected."""

    node_id: UUID
    issue_type: str
    affected_period_start: str
    affected_period_end: str
    quality_score: float
    details: str

    @property
    def event_type(self) -> str:
        return "data_quality_issue"

    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "node_id": str(self.node_id),
            "issue_type": self.issue_type,
            "affected_period_start": self.affected_period_start,
            "affected_period_end": self.affected_period_end,
            "quality_score": self.quality_score,
            "details": self.details,
        }

"""Data Transfer Objects for sensor readings."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID


@dataclass
class CreateSensorReadingDTO:
    """DTO for creating a new sensor reading."""
    node_id: UUID
    sensor_type: str
    timestamp: datetime
    measurements: Dict[str, float]  # e.g., {"temperature": 25.5, "flow_rate": 10.2}


@dataclass
class SensorReadingDTO:
    """DTO for sensor reading data."""
    id: UUID
    node_id: UUID
    node_name: str
    sensor_type: str
    timestamp: datetime
    temperature: Optional[float]
    flow_rate: Optional[float]
    pressure: Optional[float]
    volume: Optional[float]
    is_anomalous: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class SensorReadingFilterDTO:
    """DTO for filtering sensor readings."""
    node_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    sensor_types: Optional[list[str]] = None
    anomalous_only: bool = False
    limit: Optional[int] = None
    offset: Optional[int] = None
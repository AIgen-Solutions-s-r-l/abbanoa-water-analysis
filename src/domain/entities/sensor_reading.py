from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from src.domain.entities.base import Entity
from src.domain.value_objects.measurements import FlowRate, Pressure, Temperature, Volume
from src.domain.value_objects.sensor_type import SensorType


class SensorReading(Entity):
    """Domain entity representing a sensor reading at a specific point in time."""

    def __init__(
        self,
        node_id: UUID,
        sensor_type: SensorType,
        timestamp: datetime,
        temperature: Optional[Temperature] = None,
        flow_rate: Optional[FlowRate] = None,
        pressure: Optional[Pressure] = None,
        volume: Optional[Volume] = None,
        id: Optional[UUID] = None,
    ) -> None:
        super().__init__(id)
        self._node_id = node_id
        self._sensor_type = sensor_type
        self._timestamp = timestamp
        self._temperature = temperature
        self._flow_rate = flow_rate
        self._pressure = pressure
        self._volume = volume
        self._validate()

    def _validate(self) -> None:
        """Validate sensor reading business rules."""
        if not self._node_id:
            raise ValueError("Node ID is required")
        
        if not self._timestamp:
            raise ValueError("Timestamp is required")
        
        # At least one measurement must be present
        measurements = [self._temperature, self._flow_rate, self._pressure, self._volume]
        if not any(measurements):
            raise ValueError("At least one measurement must be provided")

    @property
    def node_id(self) -> UUID:
        return self._node_id

    @property
    def sensor_type(self) -> SensorType:
        return self._sensor_type

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def temperature(self) -> Optional[Temperature]:
        return self._temperature

    @property
    def flow_rate(self) -> Optional[FlowRate]:
        return self._flow_rate

    @property
    def pressure(self) -> Optional[Pressure]:
        return self._pressure

    @property
    def volume(self) -> Optional[Volume]:
        return self._volume

    def is_anomalous(self, threshold: float = 3.0) -> bool:
        """Check if any measurement is anomalous based on standard deviation threshold."""
        # This would be implemented with actual anomaly detection logic
        # For now, returning False as placeholder
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert sensor reading to dictionary representation."""
        data = {
            "id": str(self.id),
            "node_id": str(self._node_id),
            "sensor_type": self._sensor_type.value,
            "timestamp": self._timestamp.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        
        if self._temperature:
            data["temperature"] = self._temperature.to_dict()
        if self._flow_rate:
            data["flow_rate"] = self._flow_rate.to_dict()
        if self._pressure:
            data["pressure"] = self._pressure.to_dict()
        if self._volume:
            data["volume"] = self._volume.to_dict()
            
        return data
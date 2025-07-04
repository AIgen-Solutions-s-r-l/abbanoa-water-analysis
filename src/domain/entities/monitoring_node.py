from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.domain.entities.base import Entity
from src.domain.entities.sensor_reading import SensorReading
from src.domain.value_objects.location import NodeLocation
from src.domain.value_objects.node_status import NodeStatus


class MonitoringNode(Entity):
    """Domain entity representing a monitoring node in the water infrastructure."""

    def __init__(
        self,
        name: str,
        location: NodeLocation,
        node_type: str,
        status: NodeStatus = NodeStatus.ACTIVE,
        description: Optional[str] = None,
        id: Optional[UUID] = None,
    ) -> None:
        super().__init__(id)
        self._name = name
        self._location = location
        self._node_type = node_type
        self._status = status
        self._description = description
        self._readings: List[SensorReading] = []
        self._validate()

    def _validate(self) -> None:
        """Validate monitoring node business rules."""
        if not self._name or not self._name.strip():
            raise ValueError("Node name is required")

        if not self._location:
            raise ValueError("Node location is required")

        if not self._node_type:
            raise ValueError("Node type is required")

    @property
    def name(self) -> str:
        return self._name

    @property
    def location(self) -> NodeLocation:
        return self._location

    @property
    def node_type(self) -> str:
        return self._node_type

    @property
    def status(self) -> NodeStatus:
        return self._status

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def readings(self) -> List[SensorReading]:
        return self._readings.copy()

    def add_reading(self, reading: SensorReading) -> None:
        """Add a sensor reading to this node."""
        if reading.node_id != self.id:
            raise ValueError("Reading node ID does not match this node")

        self._readings.append(reading)
        self.update_timestamp()

    def get_latest_reading(self) -> Optional[SensorReading]:
        """Get the most recent sensor reading."""
        if not self._readings:
            return None

        return max(self._readings, key=lambda r: r.timestamp)

    def get_readings_in_range(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorReading]:
        """Get readings within a specific time range."""
        return [r for r in self._readings if start_time <= r.timestamp <= end_time]

    def activate(self) -> None:
        """Activate the monitoring node."""
        if self._status == NodeStatus.ACTIVE:
            raise ValueError("Node is already active")

        self._status = NodeStatus.ACTIVE
        self.update_timestamp()

    def deactivate(self) -> None:
        """Deactivate the monitoring node."""
        if self._status == NodeStatus.INACTIVE:
            raise ValueError("Node is already inactive")

        self._status = NodeStatus.INACTIVE
        self.update_timestamp()

    def mark_maintenance(self) -> None:
        """Mark node as under maintenance."""
        self._status = NodeStatus.MAINTENANCE
        self.update_timestamp()

    def is_operational(self) -> bool:
        """Check if node is operational (active and not in maintenance)."""
        return self._status == NodeStatus.ACTIVE

    def to_dict(self) -> Dict[str, Any]:
        """Convert monitoring node to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self._name,
            "location": self._location.to_dict(),
            "node_type": self._node_type,
            "status": self._status.value,
            "description": self._description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "reading_count": len(self._readings),
        }

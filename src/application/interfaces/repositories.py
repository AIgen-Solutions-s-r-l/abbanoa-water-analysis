"""Repository interfaces for the application layer."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.entities.monitoring_node import MonitoringNode
from src.domain.entities.sensor_reading import SensorReading
from src.domain.entities.water_network import WaterNetwork


class ISensorReadingRepository(ABC):
    """Interface for sensor reading repository."""

    @abstractmethod
    async def add(self, reading: SensorReading) -> None:
        """Add a new sensor reading."""
        pass

    @abstractmethod
    async def get_by_id(self, reading_id: UUID) -> Optional[SensorReading]:
        """Get a sensor reading by ID."""
        pass

    @abstractmethod
    async def get_by_node_id(
        self,
        node_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[SensorReading]:
        """Get sensor readings for a specific node."""
        pass

    @abstractmethod
    async def get_latest_by_node(self, node_id: UUID) -> Optional[SensorReading]:
        """Get the latest sensor reading for a node."""
        pass

    @abstractmethod
    async def delete_by_id(self, reading_id: UUID) -> None:
        """Delete a sensor reading by ID."""
        pass


class IMonitoringNodeRepository(ABC):
    """Interface for monitoring node repository."""

    @abstractmethod
    async def add(self, node: MonitoringNode) -> None:
        """Add a new monitoring node."""
        pass

    @abstractmethod
    async def get_by_id(self, node_id: UUID) -> Optional[MonitoringNode]:
        """Get a monitoring node by ID."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[MonitoringNode]:
        """Get a monitoring node by name."""
        pass

    @abstractmethod
    async def get_all(
        self,
        active_only: bool = False,
        node_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[MonitoringNode]:
        """Get all monitoring nodes with optional filters."""
        pass

    @abstractmethod
    async def update(self, node: MonitoringNode) -> None:
        """Update an existing monitoring node."""
        pass

    @abstractmethod
    async def delete_by_id(self, node_id: UUID) -> None:
        """Delete a monitoring node by ID."""
        pass


class IWaterNetworkRepository(ABC):
    """Interface for water network repository."""

    @abstractmethod
    async def add(self, network: WaterNetwork) -> None:
        """Add a new water network."""
        pass

    @abstractmethod
    async def get_by_id(self, network_id: UUID) -> Optional[WaterNetwork]:
        """Get a water network by ID."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[WaterNetwork]:
        """Get a water network by name."""
        pass

    @abstractmethod
    async def get_by_region(self, region: str) -> List[WaterNetwork]:
        """Get all water networks in a region."""
        pass

    @abstractmethod
    async def get_all(self) -> List[WaterNetwork]:
        """Get all water networks."""
        pass

    @abstractmethod
    async def update(self, network: WaterNetwork) -> None:
        """Update an existing water network."""
        pass

    @abstractmethod
    async def delete_by_id(self, network_id: UUID) -> None:
        """Delete a water network by ID."""
        pass

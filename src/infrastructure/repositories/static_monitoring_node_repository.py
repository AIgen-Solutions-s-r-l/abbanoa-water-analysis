"""Static monitoring node repository for demo purposes."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from src.application.interfaces.repositories import IMonitoringNodeRepository
from src.domain.entities.monitoring_node import MonitoringNode
from src.domain.entities.water_network import WaterNetwork
from src.domain.value_objects.location import Location
from src.domain.value_objects.sensor_type import SensorType


class StaticMonitoringNodeRepository(IMonitoringNodeRepository):
    """Static repository that returns hardcoded monitoring nodes."""
    
    def __init__(self, connection=None):
        """Initialize with static nodes."""
        self.nodes = [
            MonitoringNode(
                id=UUID('00000000-0000-0000-0000-000000000001'),
                network_id=UUID('00000000-0000-0000-0000-000000000099'),
                name="SELARGIUS NODO VIA SANT ANNA",
                node_type="SENSOR",
                location=Location(latitude=39.2238, longitude=9.1422),
                installation_date=datetime(2020, 1, 1),
                is_active=True,
                metadata={"node_id": "node-santanna"}
            ),
            MonitoringNode(
                id=UUID('00000000-0000-0000-0000-000000000002'),
                network_id=UUID('00000000-0000-0000-0000-000000000099'),
                name="SELARGIUS NODO VIA SENECA",
                node_type="SENSOR",
                location=Location(latitude=39.2238, longitude=9.1422),
                installation_date=datetime(2020, 1, 1),
                is_active=True,
                metadata={"node_id": "node-seneca"}
            ),
            MonitoringNode(
                id=UUID('00000000-0000-0000-0000-000000000003'),
                network_id=UUID('00000000-0000-0000-0000-000000000099'),
                name="SELARGIUS SERBATOIO",
                node_type="TANK",
                location=Location(latitude=39.2238, longitude=9.1422),
                installation_date=datetime(2020, 1, 1),
                is_active=True,
                metadata={"node_id": "node-serbatoio"}
            ),
            MonitoringNode(
                id=UUID('00000000-0000-0000-0000-000000000004'),
                network_id=UUID('00000000-0000-0000-0000-000000000099'),
                name="QUARTUCCIU SERBATOIO CUCCURU LINU",
                node_type="TANK",
                location=Location(latitude=39.2238, longitude=9.1422),
                installation_date=datetime(2020, 1, 1),
                is_active=True,
                metadata={"node_id": "node-cuccuru"}
            )
        ]
    
    async def create(self, monitoring_node: MonitoringNode) -> MonitoringNode:
        """Create not implemented for static repository."""
        raise NotImplementedError("Static repository is read-only")
    
    async def get_by_id(self, node_id: UUID) -> Optional[MonitoringNode]:
        """Get node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    async def get_by_network_id(
        self, network_id: UUID, active_only: bool = True
    ) -> List[MonitoringNode]:
        """Get nodes by network ID."""
        nodes = [n for n in self.nodes if n.network_id == network_id]
        if active_only:
            nodes = [n for n in nodes if n.is_active]
        return nodes
    
    async def get_all(self, active_only: bool = True) -> List[MonitoringNode]:
        """Get all nodes."""
        if active_only:
            return [n for n in self.nodes if n.is_active]
        return self.nodes.copy()
    
    async def get_by_type(
        self, node_type: str, active_only: bool = True
    ) -> List[MonitoringNode]:
        """Get nodes by type."""
        nodes = [n for n in self.nodes if n.node_type == node_type]
        if active_only:
            nodes = [n for n in nodes if n.is_active]
        return nodes
    
    async def update(self, monitoring_node: MonitoringNode) -> MonitoringNode:
        """Update not implemented for static repository."""
        raise NotImplementedError("Static repository is read-only")
    
    async def delete(self, node_id: UUID) -> bool:
        """Delete not implemented for static repository."""
        raise NotImplementedError("Static repository is read-only")
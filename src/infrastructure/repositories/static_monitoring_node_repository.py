"""Static monitoring node repository for demo purposes."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from src.application.interfaces.repositories import IMonitoringNodeRepository
from src.domain.entities.monitoring_node import MonitoringNode
from src.domain.value_objects.location import Coordinates, NodeLocation
from src.domain.value_objects.node_status import NodeStatus


class StaticMonitoringNodeRepository(IMonitoringNodeRepository):
    """Static repository that returns hardcoded monitoring nodes."""

    def __init__(self, connection=None):
        """Initialize with static nodes."""
        self.nodes = [
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                name="SELARGIUS NODO VIA SANT ANNA",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2238, longitude=9.1422),
                ),
                status=NodeStatus.ACTIVE,
                description="Via Sant'Anna monitoring node",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000002"),
                name="SELARGIUS NODO VIA SENECA",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2238, longitude=9.1422),
                ),
                status=NodeStatus.ACTIVE,
                description="Via Seneca monitoring node",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000003"),
                name="SELARGIUS SERBATOIO",
                node_type="TANK",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2238, longitude=9.1422),
                ),
                status=NodeStatus.ACTIVE,
                description="Selargius water tank",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000004"),
                name="QUARTUCCIU SERBATOIO CUCCURU LINU",
                node_type="TANK",
                location=NodeLocation(
                    site_name="Quartucciu",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2238, longitude=9.1422),
                ),
                status=NodeStatus.ACTIVE,
                description="Cuccuru Linu water tank",
            ),
        ]

    async def add(self, node: MonitoringNode) -> None:
        """Add not implemented for static repository."""
        raise NotImplementedError("Static repository is read-only")

    async def get_by_id(self, node_id: UUID) -> Optional[MonitoringNode]:
        """Get node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    async def get_by_name(self, name: str) -> Optional[MonitoringNode]:
        """Get node by name."""
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    async def get_all(
        self,
        active_only: bool = False,
        node_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[MonitoringNode]:
        """Get all nodes with optional filters."""
        nodes = self.nodes.copy()

        if active_only:
            nodes = [n for n in nodes if n.status == NodeStatus.ACTIVE]

        if node_type:
            nodes = [n for n in nodes if n.node_type == node_type]

        if location:
            nodes = [
                n for n in nodes if location.lower() in n.location.site_name.lower()
            ]

        return nodes

    async def update(self, node: MonitoringNode) -> None:
        """Update not implemented for static repository."""
        raise NotImplementedError("Static repository is read-only")

    async def delete_by_id(self, node_id: UUID) -> None:
        """Delete not implemented for static repository."""
        raise NotImplementedError("Static repository is read-only")

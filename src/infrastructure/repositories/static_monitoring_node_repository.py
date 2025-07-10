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
        """Initialize with static nodes based on actual data."""
        self.nodes = [
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                name="NODE 281492 - Primary Monitoring Station",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2238, longitude=9.1422),
                ),
                status=NodeStatus.ACTIVE,
                description="Primary monitoring node with highest data volume - Node ID 281492",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000002"),
                name="NODE 211514 - Secondary Monitoring Station",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2245, longitude=9.1430),
                ),
                status=NodeStatus.ACTIVE,
                description="Secondary monitoring node - Node ID 211514",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000003"),
                name="NODE 288400 - Distribution Point A",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2250, longitude=9.1435),
                ),
                status=NodeStatus.ACTIVE,
                description="Distribution monitoring point A - Node ID 288400",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000004"),
                name="NODE 288399 - Distribution Point B",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2255, longitude=9.1440),
                ),
                status=NodeStatus.ACTIVE,
                description="Distribution monitoring point B - Node ID 288399",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000005"),
                name="NODE 215542 - Network Junction C",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2260, longitude=9.1445),
                ),
                status=NodeStatus.ACTIVE,
                description="Network junction monitoring point C - Node ID 215542",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000006"),
                name="NODE 273933 - Supply Control Point",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2265, longitude=9.1450),
                ),
                status=NodeStatus.ACTIVE,
                description="Supply control monitoring point - Node ID 273933",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000007"),
                name="NODE 215600 - Pressure Regulation Station",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2270, longitude=9.1455),
                ),
                status=NodeStatus.ACTIVE,
                description="Pressure regulation monitoring station - Node ID 215600",
            ),
            MonitoringNode(
                id=UUID("00000000-0000-0000-0000-000000000008"),
                name="NODE 287156 - Remote Monitoring Point",
                node_type="SENSOR",
                location=NodeLocation(
                    site_name="Selargius",
                    area="Sardinia",
                    coordinates=Coordinates(latitude=39.2275, longitude=9.1460),
                ),
                status=NodeStatus.ACTIVE,
                description="Remote monitoring point - Node ID 287156",
            ),
        ]

    async def add(self, node: MonitoringNode) -> None:
        """Add a new monitoring node."""
        if node.id is None:
            node.id = uuid4()
        self.nodes.append(node)

    async def get_by_id(self, node_id: UUID) -> Optional[MonitoringNode]:
        """Get a monitoring node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    async def get_by_name(self, name: str) -> Optional[MonitoringNode]:
        """Get a monitoring node by name."""
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
        """Get all monitoring nodes with optional filters."""
        nodes = self.nodes.copy()
        
        if active_only:
            nodes = [node for node in nodes if node.status == NodeStatus.ACTIVE]
        
        if node_type:
            nodes = [node for node in nodes if node.node_type == node_type]
        
        if location:
            nodes = [
                node for node in nodes 
                if location.lower() in node.location.site_name.lower()
            ]
        
        return nodes

    async def update(self, node: MonitoringNode) -> None:
        """Update an existing monitoring node."""
        for i, existing_node in enumerate(self.nodes):
            if existing_node.id == node.id:
                self.nodes[i] = node
                return
        
        # If node doesn't exist, add it
        await self.add(node)

    async def delete_by_id(self, node_id: UUID) -> None:
        """Delete a monitoring node by ID."""
        for i, node in enumerate(self.nodes):
            if node.id == node_id:
                del self.nodes[i]
                return

    # Additional convenience methods
    async def create(self, node: MonitoringNode) -> MonitoringNode:
        """Create a new monitoring node."""
        await self.add(node)
        return node

    async def delete(self, node_id: UUID) -> bool:
        """Delete a monitoring node."""
        for i, node in enumerate(self.nodes):
            if node.id == node_id:
                del self.nodes[i]
                return True
        return False

    async def find_by_location(self, location: NodeLocation) -> List[MonitoringNode]:
        """Find monitoring nodes by location."""
        return [
            node for node in self.nodes 
            if node.location.site_name == location.site_name
        ]

    async def find_by_status(self, status: NodeStatus) -> List[MonitoringNode]:
        """Find monitoring nodes by status."""
        return [node for node in self.nodes if node.status == status]

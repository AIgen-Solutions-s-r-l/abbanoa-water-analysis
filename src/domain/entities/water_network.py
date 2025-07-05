from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from src.domain.entities.base import Entity
from src.domain.entities.monitoring_node import MonitoringNode
from src.domain.value_objects.measurements import FlowRate, Volume


class WaterNetwork(Entity):
    """Domain entity representing a water distribution network."""

    def __init__(
        self,
        name: str,
        region: str,
        description: Optional[str] = None,
        id: Optional[UUID] = None,
    ) -> None:
        super().__init__(id)
        self._name = name
        self._region = region
        self._description = description
        self._nodes: Dict[UUID, MonitoringNode] = {}
        self._connections: Set[tuple[UUID, UUID]] = set()
        self._validate()

    def _validate(self) -> None:
        """Validate water network business rules."""
        if not self._name or not self._name.strip():
            raise ValueError("Network name is required")

        if not self._region or not self._region.strip():
            raise ValueError("Region is required")

    @property
    def name(self) -> str:
        return self._name

    @property
    def region(self) -> str:
        return self._region

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def nodes(self) -> List[MonitoringNode]:
        return list(self._nodes.values())

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def active_node_count(self) -> int:
        return sum(1 for node in self._nodes.values() if node.is_operational())

    def add_node(self, node: MonitoringNode) -> None:
        """Add a monitoring node to the network."""
        if node.id in self._nodes:
            raise ValueError(f"Node {node.id} already exists in network")

        self._nodes[node.id] = node
        self.update_timestamp()

    def remove_node(self, node_id: UUID) -> None:
        """Remove a monitoring node from the network."""
        if node_id not in self._nodes:
            raise ValueError(f"Node {node_id} not found in network")

        # Remove all connections involving this node
        self._connections = {conn for conn in self._connections if node_id not in conn}

        del self._nodes[node_id]
        self.update_timestamp()

    def get_node(self, node_id: UUID) -> Optional[MonitoringNode]:
        """Get a monitoring node by ID."""
        return self._nodes.get(node_id)

    def connect_nodes(self, from_node_id: UUID, to_node_id: UUID) -> None:
        """Create a connection between two nodes."""
        if from_node_id not in self._nodes:
            raise ValueError(f"From node {from_node_id} not found")

        if to_node_id not in self._nodes:
            raise ValueError(f"To node {to_node_id} not found")

        if from_node_id == to_node_id:
            raise ValueError("Cannot connect node to itself")

        connection = (from_node_id, to_node_id)
        if connection in self._connections:
            raise ValueError("Connection already exists")

        self._connections.add(connection)
        self.update_timestamp()

    def disconnect_nodes(self, from_node_id: UUID, to_node_id: UUID) -> None:
        """Remove a connection between two nodes."""
        connection = (from_node_id, to_node_id)
        if connection not in self._connections:
            raise ValueError("Connection does not exist")

        self._connections.remove(connection)
        self.update_timestamp()

    def get_connected_nodes(self, node_id: UUID) -> List[UUID]:
        """Get all nodes connected to a specific node."""
        if node_id not in self._nodes:
            raise ValueError(f"Node {node_id} not found")

        connected = []
        for from_id, to_id in self._connections:
            if from_id == node_id:
                connected.append(to_id)
            elif to_id == node_id:
                connected.append(from_id)

        return connected

    def calculate_network_efficiency(
        self, start_time: datetime, end_time: datetime
    ) -> float:
        """Calculate network efficiency based on input vs output flow rates."""
        input_nodes = [
            n for n in self._nodes.values() if "input" in n.node_type.lower()
        ]
        output_nodes = [
            n for n in self._nodes.values() if "output" in n.node_type.lower()
        ]

        if not input_nodes or not output_nodes:
            return 0.0

        total_input = 0.0
        total_output = 0.0

        for node in input_nodes:
            readings = node.get_readings_in_range(start_time, end_time)
            for reading in readings:
                if reading.flow_rate:
                    total_input += reading.flow_rate.value

        for node in output_nodes:
            readings = node.get_readings_in_range(start_time, end_time)
            for reading in readings:
                if reading.flow_rate:
                    total_output += reading.flow_rate.value

        if total_input == 0:
            return 0.0

        return (total_output / total_input) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert water network to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self._name,
            "region": self._region,
            "description": self._description,
            "node_count": self.node_count,
            "active_node_count": self.active_node_count,
            "connection_count": len(self._connections),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

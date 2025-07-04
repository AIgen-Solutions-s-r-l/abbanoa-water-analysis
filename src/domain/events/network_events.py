from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

from src.domain.events.base import DomainEvent


@dataclass
class NodeAddedEvent(DomainEvent):
    """Event raised when a new node is added to the network."""
    
    network_id: UUID
    node_id: UUID
    node_name: str
    node_type: str
    location: str
    
    def __post_init__(self):
        super().__init__()
    
    @property
    def event_type(self) -> str:
        return "node_added"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "network_id": str(self.network_id),
            "node_id": str(self.node_id),
            "node_name": self.node_name,
            "node_type": self.node_type,
            "location": self.location
        }


@dataclass
class NodeRemovedEvent(DomainEvent):
    """Event raised when a node is removed from the network."""
    
    network_id: UUID
    node_id: UUID
    node_name: str
    reason: str
    
    def __post_init__(self):
        super().__init__()
    
    @property
    def event_type(self) -> str:
        return "node_removed"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "network_id": str(self.network_id),
            "node_id": str(self.node_id),
            "node_name": self.node_name,
            "reason": self.reason
        }


@dataclass
class NodeStatusChangedEvent(DomainEvent):
    """Event raised when a node's status changes."""
    
    node_id: UUID
    node_name: str
    old_status: str
    new_status: str
    reason: str
    
    def __post_init__(self):
        super().__init__()
    
    @property
    def event_type(self) -> str:
        return "node_status_changed"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "node_id": str(self.node_id),
            "node_name": self.node_name,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "reason": self.reason
        }


@dataclass
class NetworkEfficiencyCalculatedEvent(DomainEvent):
    """Event raised when network efficiency is calculated."""
    
    network_id: UUID
    period_start: str
    period_end: str
    efficiency_percentage: float
    total_input: float
    total_output: float
    loss_percentage: float
    
    def __post_init__(self):
        super().__init__()
    
    @property
    def event_type(self) -> str:
        return "network_efficiency_calculated"
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "network_id": str(self.network_id),
            "period_start": self.period_start,
            "period_end": self.period_end,
            "efficiency_percentage": self.efficiency_percentage,
            "total_input": self.total_input,
            "total_output": self.total_output,
            "loss_percentage": self.loss_percentage
        }
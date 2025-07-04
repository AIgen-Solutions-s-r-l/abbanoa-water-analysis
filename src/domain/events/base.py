from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4


class DomainEvent(ABC):
    """Base class for all domain events."""

    def __init__(self):
        self.event_id: UUID = uuid4()
        self.occurred_at: datetime = datetime.utcnow()
        self.aggregate_id: UUID = uuid4()

    @property
    @abstractmethod
    def event_type(self) -> str:
        """Return the type of the event."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "aggregate_id": str(self.aggregate_id),
            "data": self._get_event_data(),
        }

    @abstractmethod
    def _get_event_data(self) -> Dict[str, Any]:
        """Get event-specific data."""
        pass

"""Event bus interface for domain event handling."""

from abc import ABC, abstractmethod
from typing import Callable, List, Type

from src.domain.events.base import DomainEvent


class IEventBus(ABC):
    """Interface for event bus to handle domain events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        pass

    @abstractmethod
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple domain events."""
        pass

    @abstractmethod
    def subscribe(
        self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]
    ) -> None:
        """Subscribe to a specific event type."""
        pass

    @abstractmethod
    def unsubscribe(
        self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]
    ) -> None:
        """Unsubscribe from a specific event type."""
        pass

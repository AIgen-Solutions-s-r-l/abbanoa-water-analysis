"""Event bus implementation for domain events."""

import asyncio
from collections import defaultdict
from typing import Callable, Dict, List, Type

from src.application.interfaces.event_bus import IEventBus
from src.domain.events.base import DomainEvent


class InMemoryEventBus(IEventBus):
    """In-memory implementation of event bus."""

    def __init__(self) -> None:
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = defaultdict(list)

    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to all registered handlers."""
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        # Execute handlers concurrently
        if handlers:
            tasks = [self._execute_handler(handler, event) for handler in handlers]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple domain events."""
        tasks = [self.publish(event) for event in events]
        await asyncio.gather(*tasks, return_exceptions=True)

    def subscribe(
        self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]
    ) -> None:
        """Subscribe to a specific event type."""
        self._handlers[event_type].append(handler)

    def unsubscribe(
        self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]
    ) -> None:
        """Unsubscribe from a specific event type."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass  # Handler not in list

    async def _execute_handler(
        self, handler: Callable[[DomainEvent], None], event: DomainEvent
    ) -> None:
        """Execute a handler, handling both sync and async handlers."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                # Run sync handler in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, handler, event)
        except Exception as e:
            # Log error but don't propagate - other handlers should still execute
            print(f"Error in event handler: {e}")

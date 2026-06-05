"""Abstract event bus interface."""

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from odin_backend.models.event import Event, EventType

EventHandler = Callable[[Event], Awaitable[None]]


class EventBus(ABC):
    """Publish/subscribe contract for ODIN events."""

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def publish(self, event: Event) -> None: ...

    @abstractmethod
    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None: ...

    @abstractmethod
    async def subscribe_all(self, handler: EventHandler) -> None: ...


class InMemoryEventBus(EventBus):
    """Local event bus for development and tests."""

    def __init__(self) -> None:
        self._handlers: dict[EventType | None, list[EventHandler]] = defaultdict(list)
        self._connected = False

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._handlers.clear()
        self._connected = False

    async def publish(self, event: Event) -> None:
        handlers = list(self._handlers.get(event.type, [])) + list(self._handlers.get(None, []))
        for handler in handlers:
            await handler(event)

    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def subscribe_all(self, handler: EventHandler) -> None:
        self._handlers[None].append(handler)

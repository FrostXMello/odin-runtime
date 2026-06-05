"""Central event hub for SSE broadcasting."""

import asyncio
from collections import deque
from typing import Any

from odin_backend.models.event import Event


class EventHub:
    """Buffers events and fans out to SSE subscribers."""

    def __init__(self, buffer_size: int = 500) -> None:
        self._buffer: deque[dict[str, Any]] = deque(maxlen=buffer_size)
        self._subscribers: list[asyncio.Queue[dict[str, Any]]] = []

    async def publish(self, event: Event) -> None:
        data = event.model_dump(mode="json")
        self._buffer.append(data)
        dead: list[asyncio.Queue] = []
        for q in self._subscribers:
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self._subscribers.remove(q)

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        q: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=100)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self._subscribers:
            self._subscribers.remove(q)

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return list(self._buffer)[-limit:]

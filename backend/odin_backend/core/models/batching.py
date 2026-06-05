"""Concurrent inference batch scheduling."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine
from uuid import uuid4


@dataclass(order=True)
class InferenceRequest:
    priority: int
    request_id: str = field(compare=False, default_factory=lambda: str(uuid4()))
    model: str = field(compare=False, default="")
    payload: dict[str, Any] = field(compare=False, default_factory=dict)
    cancelled: bool = field(compare=False, default=False)


class InferenceBatcher:
    def __init__(self, *, max_concurrent: int = 2) -> None:
        self._queue: asyncio.PriorityQueue[InferenceRequest] = asyncio.PriorityQueue()
        self._max_concurrent = max_concurrent
        self._active = 0
        self._cancelled: set[str] = set()

    async def submit(
        self,
        coro_factory: Callable[[InferenceRequest], Coroutine[Any, Any, Any]],
        *,
        model: str,
        priority: int = 5,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        req = InferenceRequest(priority=priority, model=model, payload=payload or {})
        await self._queue.put(req)
        while self._active >= self._max_concurrent:
            await asyncio.sleep(0.01)
        if req.request_id in self._cancelled:
            self._cancelled.discard(req.request_id)
            raise asyncio.CancelledError(req.request_id)
        self._active += 1
        try:
            return await coro_factory(req)
        finally:
            self._active -= 1

    def cancel(self, request_id: str) -> None:
        self._cancelled.add(request_id)

    @property
    def queue_depth(self) -> int:
        return self._queue.qsize()

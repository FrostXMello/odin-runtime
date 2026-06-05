"""Concurrent inference throttling."""

from __future__ import annotations

import asyncio


class InferenceLimiter:
    def __init__(self, *, max_concurrent: int = 2) -> None:
        self._sem = asyncio.Semaphore(max_concurrent)
        self._max = max_concurrent

    async def acquire(self) -> None:
        await self._sem.acquire()

    def release(self) -> None:
        self._sem.release()

    @property
    def max_concurrent(self) -> int:
        return self._max

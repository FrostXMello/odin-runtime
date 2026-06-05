"""Mission-level async locks for graph mutation safety."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class MissionLockManager:
    def __init__(self) -> None:
        self._locks: dict[str, asyncio.Lock] = {}
        self._meta: dict[str, asyncio.Lock] = {}

    def _lock(self, mission_id: str) -> asyncio.Lock:
        if mission_id not in self._locks:
            self._locks[mission_id] = asyncio.Lock()
        return self._locks[mission_id]

    @asynccontextmanager
    async def mission(self, mission_id: str) -> AsyncIterator[None]:
        lock = self._lock(mission_id)
        await lock.acquire()
        try:
            yield
        finally:
            lock.release()

    @asynccontextmanager
    async def reconciliation(self, mission_id: str) -> AsyncIterator[None]:
        if mission_id not in self._meta:
            self._meta[mission_id] = asyncio.Lock()
        lock = self._meta[mission_id]
        await lock.acquire()
        try:
            yield
        finally:
            lock.release()

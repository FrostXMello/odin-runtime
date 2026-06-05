"""Evict idle models under memory pressure."""

from __future__ import annotations

import time
from typing import Any


class ModelEvictionPolicy:
    def __init__(self, *, idle_seconds: int = 600) -> None:
        self._idle_seconds = idle_seconds
        self._last_used: dict[str, float] = {}

    def touch(self, model_name: str) -> None:
        self._last_used[model_name] = time.time()

    def candidates(self, loaded: list[str]) -> list[str]:
        now = time.time()
        return [m for m in loaded if now - self._last_used.get(m, 0) > self._idle_seconds]

    async def evict(self, app: Any, models: list[str]) -> list[str]:
        evicted: list[str] = []
        for m in models:
            if await app.model_manager.unload(m):
                evicted.append(m)
        return evicted

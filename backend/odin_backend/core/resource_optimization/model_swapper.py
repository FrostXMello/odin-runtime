"""Adaptive model unloading under pressure."""

from __future__ import annotations

from typing import Any


class ModelSwapper:
    def __init__(self) -> None:
        self._evicted: list[str] = []

    async def evict_under_pressure(self, app: Any) -> list[str]:
        evicted = []
        if hasattr(app, "local_ai"):
            for model in list(app.local_ai._loaded):
                await app.local_ai.evict(model)
                evicted.append(model)
                self._evicted.append(model)
                break
        return evicted

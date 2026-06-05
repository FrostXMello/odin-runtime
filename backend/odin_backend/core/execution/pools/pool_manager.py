"""Execution pool isolation."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PoolMetrics:
    active: int = 0
    completed: int = 0
    failed: int = 0
    rejected: int = 0


class ExecutionPool:
    def __init__(self, name: str, *, max_concurrent: int = 4) -> None:
        self.name = name
        self.max_concurrent = max_concurrent
        self._sem = asyncio.Semaphore(max_concurrent)
        self.metrics = PoolMetrics()

    async def run(self, coro_factory: Callable[[], Awaitable[Any]]) -> Any:
        if self._sem.locked() and self.metrics.active >= self.max_concurrent:
            self.metrics.rejected += 1
            raise RuntimeError(f"pool {self.name} at capacity")
        async with self._sem:
            self.metrics.active += 1
            try:
                result = await coro_factory()
                self.metrics.completed += 1
                return result
            except Exception:
                self.metrics.failed += 1
                raise
            finally:
                self.metrics.active -= 1


class ExecutionPoolManager:
    def __init__(self, app: Any) -> None:
        settings = app.settings
        max_c = settings.execution_pool_max_concurrent
        self._pools: dict[str, ExecutionPool] = {
            "local": ExecutionPool("local", max_concurrent=max_c),
            "subprocess": ExecutionPool("subprocess", max_concurrent=max_c),
            "container": ExecutionPool("container", max_concurrent=max(1, max_c // 2)),
        }
        self._default = settings.execution_pool_default

    def get(self, name: str | None = None) -> ExecutionPool:
        return self._pools.get(name or self._default, self._pools["local"])

    def route_pool(self, capability: str) -> ExecutionPool:
        if capability.startswith("shell."):
            return self._pools["subprocess"]
        if capability.startswith("workflow."):
            return self._pools["subprocess"]
        return self._pools["local"]

    @property
    def metrics(self) -> dict[str, dict[str, int]]:
        return {
            name: {
                "active": p.metrics.active,
                "completed": p.metrics.completed,
                "failed": p.metrics.failed,
                "rejected": p.metrics.rejected,
                "max_concurrent": p.max_concurrent,
            }
            for name, p in self._pools.items()
        }

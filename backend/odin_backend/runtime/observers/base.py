"""Base runtime observer — throttled, deduplicated perceptions."""

import asyncio
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Any

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class BaseRuntimeObserver(ABC):
    name: str = "base"
    interval_seconds: float = 10.0
    min_emit_interval: float = 5.0

    def __init__(self, perception_engine: Any) -> None:
        self._perception = perception_engine
        self._task: asyncio.Task | None = None
        self._running = False
        self._last_emit: dict[str, float] = {}
        self._seen: dict[str, float] = {}
        self._dedupe_window = 60.0

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("runtime_observer_started", observer=self.name)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        while self._running:
            try:
                records = await self.poll()
                for record in records:
                    if self._should_emit(record):
                        await self._perception.ingest(record)
            except Exception as exc:
                logger.exception("observer_error", observer=self.name, error=str(exc))
            await asyncio.sleep(self.interval_seconds)

    @abstractmethod
    async def poll(self) -> list[Any]:
        ...

    def _should_emit(self, record: Any) -> bool:
        key = f"{self.name}:{record.category.value}"
        now = time.monotonic()
        if now - self._last_emit.get(key, 0.0) < self.min_emit_interval:
            return False
        digest = hashlib.sha256(record.summary.encode()).hexdigest()[:12]
        if digest in self._seen and now - self._seen[digest] < self._dedupe_window:
            return False
        self._last_emit[key] = now
        self._seen[digest] = now
        return True

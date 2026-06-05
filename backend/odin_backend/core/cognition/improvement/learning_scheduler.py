"""Learning job scheduler."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class LearningScheduler:
    def __init__(self, app: Any, *, interval_seconds: float = 300.0) -> None:
        self._app = app
        self._interval = interval_seconds
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        async def _loop() -> None:
            while True:
                try:
                    loop = getattr(self._app, "improvement_loop", None)
                    if loop:
                        await loop.run_cycle()
                except Exception as exc:
                    logger.warning("learning_scheduler_error", error=str(exc))
                await asyncio.sleep(self._interval)

        self._task = asyncio.create_task(_loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

"""Action scheduling with pacing."""

from __future__ import annotations

import asyncio
from typing import Any


class ActionScheduler:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def enqueue(self, action_id: str) -> None:
        await self._queue.put(action_id)

    async def _loop(self) -> None:
        pace = getattr(self._app.settings, "action_pace_ms", 250) / 1000.0
        runtime = self._app.action_runtime
        while self._running:
            try:
                action_id = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            if runtime.emergency_stopped:
                continue
            await runtime.execute_approved(action_id)
            await asyncio.sleep(pace)

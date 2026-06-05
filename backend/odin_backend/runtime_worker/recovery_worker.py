"""Recovery worker — orphan repair, stale leases, deadletter replay."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.monitoring.logging import get_logger
from odin_backend.runtime_worker.heartbeat import WorkerHeartbeat
from odin_backend.runtime_worker.registration import WorkerRegistration

logger = get_logger(__name__)


class RecoveryWorker:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._task: asyncio.Task | None = None
        self._heartbeat = WorkerHeartbeat(app)
        self._registration = WorkerRegistration(app)

    async def start(self) -> None:
        await self._registration.register(role="recovery")
        await self._heartbeat.start()
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        await self._heartbeat.stop()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        interval = max(30.0, self._app.settings.execution_recovery_interval_seconds)
        while True:
            rec = self._app.distributed_recovery
            await rec.recover_abandoned_leases()
            if self._app.settings.execution_engine_enabled:
                await self._app.execution_engine.recover_stuck()
            await asyncio.sleep(interval)

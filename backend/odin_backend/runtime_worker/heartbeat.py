"""Worker heartbeat loop."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class WorkerHeartbeat:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        reg = self._app.worker_registry
        interval = max(10.0, self._app.settings.runtime_heartbeat_interval_seconds)

        async def _loop() -> None:
            while True:
                q = self._app.distributed_queue
                leases = q.leases.metrics.get("leases_acquired", 0) - q.leases.metrics.get(
                    "leases_released", 0
                )
                await reg.heartbeat(active_leases=max(0, leases))
                pubsub = getattr(self._app, "distributed_pubsub", None)
                if pubsub:
                    await pubsub.publish(
                        "worker_heartbeat",
                        {"worker_id": reg.worker_id, "active_leases": leases},
                    )
                await asyncio.sleep(interval)

        self._task = asyncio.create_task(_loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

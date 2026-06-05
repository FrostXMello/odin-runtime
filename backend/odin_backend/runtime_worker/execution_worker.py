"""Execution worker — consume tasks, run capabilities, renew leases."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.monitoring.logging import get_logger
from odin_backend.runtime_worker.heartbeat import WorkerHeartbeat
from odin_backend.runtime_worker.registration import WorkerRegistration

logger = get_logger(__name__)


class ExecutionWorker:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._task: asyncio.Task | None = None
        self._heartbeat = WorkerHeartbeat(app)
        self._registration = WorkerRegistration(app)
        self._running = False

    async def start(self) -> None:
        await self._registration.register(role="execution")
        await self._heartbeat.start()
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._running = False
        await self._app.worker_registry.set_draining(True)
        await self._heartbeat.stop()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        interval = max(0.5, self._app.settings.mission_dispatch_interval_seconds)
        while self._running:
            if self._app.worker_registry._draining:
                await asyncio.sleep(interval)
                continue
            items = await self._app.distributed_queue.dequeue_missions(limit=1)
            for item in items:
                mid = item.mission_id
                if not mid:
                    continue
                router = self._app.capability_router
                cap = item.required_capability or "workflow.execute"
                target = await router.route(cap)
                if target and target.worker_id != self._app.distributed_queue.worker_id:
                    await self._app.distributed_queue.nack_mission(mid, delay=0.5)
                    continue
                self._app.mission_dispatcher.wake(mid, reason="worker_dequeue")
                token = item.fencing_token
                if token:
                    await self._app.distributed_queue.leases.renew(
                        item.queue_item_id,
                        self._app.distributed_queue.worker_id,
                        fencing_token=token,
                    )
            await asyncio.sleep(interval)

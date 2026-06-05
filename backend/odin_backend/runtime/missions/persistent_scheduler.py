"""Persistent mission scheduler — MissionScheduler-compatible API."""

from __future__ import annotations

import time
from typing import Any

from odin_backend.monitoring.logging import get_logger
from odin_backend.runtime.missions.scheduler import MissionScheduler, ScheduledMissionTick

logger = get_logger(__name__)


class PersistentMissionScheduler(MissionScheduler):
    """
    Extends in-memory scheduler with durable queue backing.

    ``schedule`` / ``pop_due`` remain sync-compatible; persistence uses async tasks.
    ``pop_due_async`` is preferred by dispatcher when available.
    """

    def __init__(self, app: Any) -> None:
        super().__init__(cooldown_seconds=app.settings.mission_cooldown_seconds)
        self._app = app
        self._pending_ack: dict[str, str] = {}

    def _distributed_queue_svc(self):
        return getattr(self._app, "distributed_queue", None)

    def schedule(self, mission_id: str, *, delay_seconds: float = 0.0, reason: str = "scheduled") -> None:
        if mission_id in self._queued_ids:
            return
        super().schedule(mission_id, delay_seconds=delay_seconds, reason=reason)
        q = self._distributed_queue_svc()
        if q:
            import asyncio

            try:
                loop = asyncio.get_running_loop()
                loop.create_task(q.enqueue_mission(mission_id, delay_seconds=delay_seconds, reason=reason))
            except RuntimeError:
                pass

    def schedule_retry(self, mission_id: str, *, delay_seconds: float | None = None) -> None:
        delay = delay_seconds if delay_seconds is not None else self._cooldown
        self.schedule(mission_id, delay_seconds=delay, reason="retry")

    async def pop_due_async(self) -> list[str]:
        q = self._distributed_queue_svc()
        if q:
            await q.requeue_expired()
            items = await q.dequeue_missions(limit=10)
            due: list[str] = []
            now = time.monotonic()
            for item in items:
                mid = item.mission_id
                if not mid:
                    continue
                if not self._cooldown_elapsed(mid, now):
                    await q.nack_mission(mid, delay=self._cooldown)
                    continue
                due.append(mid)
                self._queued_ids.discard(mid)
                self._last_tick[mid] = now
                self._pending_ack[mid] = item.queue_item_id
            if due:
                return due
        return super().pop_due()

    async def ack_dispatched(self, mission_id: str) -> None:
        q = self._distributed_queue_svc()
        if q:
            await q.ack_mission(mission_id)
        self._pending_ack.pop(mission_id, None)

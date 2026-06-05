"""Distributed queue service facade."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from odin_backend.core.queueing.acknowledgements import emit_queue_trace
from odin_backend.core.queueing.deadletter import DeadLetterQueue
from odin_backend.core.queueing.in_memory_backend import InMemoryQueueBackend
from odin_backend.core.queueing.leases import LeaseCoordinator
from odin_backend.core.queueing.queue_backend import QueueBackend
from odin_backend.core.queueing.queue_models import QueueItem
from odin_backend.core.queueing.sqlite_backend import SQLiteQueueBackend
from odin_backend.core.queueing.wake_signals import WakeSignalStore
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class DistributedQueueService:
    """Persistent queue layer for mission dispatch and task work."""

    def __init__(self, app: Any) -> None:
        self._app = app
        settings = app.settings
        self.worker_id = settings.worker_id or f"odin-{id(app) & 0xFFFF:04x}"
        if settings.queue_persist_enabled:
            from odin_backend.core.distributed.transport import create_queue_backend

            self.backend: QueueBackend = create_queue_backend(settings)
            self._sqlite = self.backend if settings.queue_backend == "sqlite" else None
        else:
            self.backend = InMemoryQueueBackend()
            self._sqlite = None
        self.leases = LeaseCoordinator(
            self.backend,
            default_lease_seconds=settings.queue_visibility_timeout_seconds,
            app=app,
        )
        self.wake_signals = WakeSignalStore(settings)
        self.deadletter = DeadLetterQueue(settings, self._sqlite) if self._sqlite else None
        self._item_by_mission: dict[str, str] = {}
        self._metrics: dict[str, int] = {
            "enqueued": 0,
            "dequeued": 0,
            "acked": 0,
            "nacked": 0,
            "deadlettered": 0,
            "replayed": 0,
        }

    async def connect(self) -> None:
        await self.backend.connect()
        await self.wake_signals.connect()
        if self.deadletter:
            await self.deadletter.connect()
        logger.info("distributed_queue_connected", worker_id=self.worker_id, persist=self._app.settings.queue_persist_enabled)

    async def disconnect(self) -> None:
        await self.backend.disconnect()
        await self.wake_signals.disconnect()
        if self.deadletter:
            await self.deadletter.disconnect()

    async def enqueue_mission(
        self,
        mission_id: str,
        *,
        delay_seconds: float = 0.0,
        reason: str = "scheduled",
        priority: int = 50,
    ) -> QueueItem:
        visible = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
        item = QueueItem(
            mission_id=mission_id,
            payload={"kind": "mission_dispatch", "mission_id": mission_id, "reason": reason},
            priority=priority,
            visible_at=visible,
            dedup_key=f"mission:{mission_id}",
            reason=reason,
        )
        saved = await self.backend.enqueue(item)
        self._item_by_mission[mission_id] = saved.queue_item_id
        self._metrics["enqueued"] += 1
        emit_queue_trace(self._app, "enqueue", message=reason, payload={"mission_id": mission_id})
        return saved

    async def dequeue_missions(self, *, limit: int = 10) -> list[QueueItem]:
        items = await self.leases.acquire(self.worker_id, limit=limit)
        self._metrics["dequeued"] += len(items)
        for item in items:
            emit_queue_trace(
                self._app,
                "dequeue",
                message=item.reason,
                payload={"mission_id": item.mission_id, "queue_item_id": item.queue_item_id},
            )
        return items

    async def ack_mission(self, mission_id: str) -> bool:
        qid = self._item_by_mission.pop(mission_id, None)
        if not qid:
            return False
        ok = await self.leases.release(qid, self.worker_id)
        if ok:
            self._metrics["acked"] += 1
        return ok

    async def nack_mission(self, mission_id: str, *, delay: float = 1.0) -> bool:
        qid = self._item_by_mission.get(mission_id)
        if not qid:
            return False
        ok = await self.leases.abandon(qid, self.worker_id, delay=delay)
        if ok:
            self._metrics["nacked"] += 1
        return ok

    async def requeue_expired(self) -> int:
        return await self.leases.requeue_stale()

    async def stats(self) -> dict[str, Any]:
        backend_stats = await self.backend.stats()
        return {
            **backend_stats,
            "worker_id": self.worker_id,
            "metrics": self._metrics,
            "lease_metrics": self.leases.metrics,
            "wake_signals": self.wake_signals.metrics(),
            "deadletter_count": self.deadletter.count if self.deadletter else 0,
        }

    async def idempotent_wake(self, mission_id: str, *, reason: str = "runtime_event") -> bool:
        if not await self.wake_signals.should_wake(mission_id, reason=reason):
            from odin_backend.core.observability.events import TraceEventKind

            obs = getattr(self._app, "observability", None)
            if obs:
                obs.tracer.record(
                    TraceEventKind.REPLAY_SUPPRESSED,
                    message="wake suppressed",
                    payload={"mission_id": mission_id, "reason": reason},
                    component="wake_signals",
                )
            return False
        await self.enqueue_mission(mission_id, delay_seconds=0.0, reason=reason)
        return True

    @property
    def metrics(self) -> dict[str, Any]:
        return dict(self._metrics)

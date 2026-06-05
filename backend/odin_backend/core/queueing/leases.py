"""Queue lease coordination with distributed fencing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from odin_backend.core.queueing.queue_backend import QueueBackend
from odin_backend.core.queueing.queue_models import QueueItem
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class LeaseCoordinator:
    """Coordinates queue item leases, stale recovery, and fencing tokens."""

    def __init__(
        self,
        backend: QueueBackend,
        *,
        default_lease_seconds: float = 60.0,
        app: Any | None = None,
    ) -> None:
        self._backend = backend
        self._default_lease = default_lease_seconds
        self._app = app
        self._active_fences: dict[str, int] = {}
        self._metrics: dict[str, int] = {
            "leases_acquired": 0,
            "leases_renewed": 0,
            "leases_released": 0,
            "stale_requeued": 0,
            "lease_conflicts": 0,
            "fence_rejected": 0,
        }

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    def fencing_token_for(self, queue_item_id: str) -> int | None:
        return self._active_fences.get(queue_item_id)

    async def acquire(
        self,
        worker_id: str,
        *,
        limit: int = 1,
        lease_seconds: float | None = None,
    ) -> list[QueueItem]:
        lease = lease_seconds or self._default_lease
        items = await self._backend.dequeue(worker_id, limit=limit, lease_seconds=lease)
        if items:
            self._metrics["leases_acquired"] += len(items)
            for item in items:
                if item.fencing_token is not None:
                    self._active_fences[item.queue_item_id] = item.fencing_token
            self._emit("lease acquire", {"count": len(items), "worker_id": worker_id})
        return items

    async def renew(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        lease_seconds: float | None = None,
        fencing_token: int | None = None,
    ) -> bool:
        token = fencing_token or self._active_fences.get(queue_item_id)
        ok = await self._backend.renew_lease(
            queue_item_id,
            worker_id,
            lease_seconds=lease_seconds or self._default_lease,
            fencing_token=token,
        )
        if ok:
            self._metrics["leases_renewed"] += 1
        else:
            self._metrics["lease_conflicts"] += 1
            self._metrics["fence_rejected"] += 1
            self._emit_fence_rejected(queue_item_id, worker_id, token)
        return ok

    async def release(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        fencing_token: int | None = None,
    ) -> bool:
        token = fencing_token or self._active_fences.get(queue_item_id)
        ok = await self._backend.ack(queue_item_id, worker_id, fencing_token=token)
        if ok:
            self._metrics["leases_released"] += 1
            self._active_fences.pop(queue_item_id, None)
            self._emit("lease release", {"queue_item_id": queue_item_id})
        else:
            self._metrics["fence_rejected"] += 1
            self._emit_fence_rejected(queue_item_id, worker_id, token)
        return ok

    async def abandon(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        delay: float = 1.0,
        fencing_token: int | None = None,
    ) -> bool:
        token = fencing_token or self._active_fences.get(queue_item_id)
        ok = await self._backend.nack(
            queue_item_id,
            worker_id,
            requeue_delay=delay,
            fencing_token=token,
        )
        if ok:
            self._active_fences.pop(queue_item_id, None)
        else:
            self._metrics["fence_rejected"] += 1
            self._emit_fence_rejected(queue_item_id, worker_id, token)
        return ok

    async def requeue_stale(self) -> int:
        count = await self._backend.requeue_expired()
        if count:
            self._metrics["stale_requeued"] += count
            self._emit("stale requeue", {"count": count})
        return count

    async def list_active_leases(self, *, limit: int = 100) -> list[dict[str, Any]]:
        stats = await self._backend.stats()
        fences = [
            {"queue_item_id": qid, "fencing_token": tok}
            for qid, tok in list(self._active_fences.items())[:limit]
        ]
        return [{"summary": stats, "metrics": self.metrics, "active_fences": fences}]

    def invalidate_stale_fence(self, queue_item_id: str) -> None:
        self._active_fences.pop(queue_item_id, None)

    def _emit_fence_rejected(
        self,
        queue_item_id: str,
        worker_id: str,
        token: int | None,
    ) -> None:
        if not self._app:
            return
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        obs.tracer.record(
            TraceEventKind.LEASE_FENCED,
            message="stale fencing token rejected",
            payload={
                "queue_item_id": queue_item_id,
                "worker_id": worker_id,
                "fencing_token": token,
            },
            component="lease_coordinator",
        )

    def _emit(self, message: str, payload: dict[str, Any]) -> None:
        if not self._app:
            return
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        obs.tracer.record(
            TraceEventKind.LEASE_RECOVERED,
            message=message,
            payload=payload,
            component="lease_coordinator",
        )

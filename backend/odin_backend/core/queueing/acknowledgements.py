"""Queue acknowledgement helpers."""

from __future__ import annotations

from typing import Any

from odin_backend.core.queueing.leases import LeaseCoordinator
from odin_backend.core.queueing.queue_models import QueueItem


async def ack_item(coordinator: LeaseCoordinator, item: QueueItem) -> bool:
    if not item.worker_id:
        return False
    return await coordinator.release(item.queue_item_id, item.worker_id)


async def nack_item(
    coordinator: LeaseCoordinator,
    item: QueueItem,
    *,
    delay: float = 0.0,
    reason: str = "nack",
) -> bool:
    if not item.worker_id:
        return False
    return await coordinator.abandon(item.queue_item_id, item.worker_id, delay=delay)


def emit_queue_trace(app: Any, kind: str, *, message: str, payload: dict | None = None) -> None:
    obs = getattr(app, "observability", None)
    if not obs:
        return
    from odin_backend.core.observability.events import TraceEventKind

    mapping = {
        "enqueue": TraceEventKind.QUEUE_ENQUEUED,
        "dequeue": TraceEventKind.TASK_REQUEUED,
        "ack": TraceEventKind.LEASE_RECOVERED,
        "nack": TraceEventKind.TASK_REQUEUED,
        "deadletter": TraceEventKind.DEADLETTERED,
        "replay": TraceEventKind.REPLAY_SUPPRESSED,
    }
    event_kind = mapping.get(kind, TraceEventKind.QUEUE_ENQUEUED)
    obs.tracer.record(event_kind, message=message, payload=payload or {}, component="queue")

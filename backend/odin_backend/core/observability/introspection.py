"""Live runtime introspection — queues, workers, bottlenecks."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.missions.lifecycle import migrate_legacy_state
from odin_backend.models.mission import MissionLifecycle
from odin_backend.models.task_graph import TaskNodeStatus


class QueueSnapshot(BaseModel):
    dispatch_queue_depth: int = 0
    retry_queue_depth: int = 0
    due_missions: list[str] = Field(default_factory=list)
    persist_enabled: bool = False
    durable_depth: int = 0
    lease_conflicts: int = 0
    stale_requeues: int = 0


class WorkerSnapshot(BaseModel):
    dispatcher_running: bool = False
    dispatcher_ticks: int = 0
    dispatcher_executions: int = 0
    worker_mode: str = "scheduler_only"
    last_tick_at: float | None = None
    worker_id: str | None = None
    runtime_workers: list[dict[str, Any]] = Field(default_factory=list)


class BottleneckReport(BaseModel):
    mission_id: str
    reason: str
    pending_tasks: int = 0
    blocked_tasks: int = 0
    state: str = ""


def queue_snapshot(app: Any) -> QueueSnapshot:
    scheduler = app.mission_worker.scheduler
    due = scheduler.peek_due_ids() if hasattr(scheduler, "peek_due_ids") else []
    snap = QueueSnapshot(
        dispatch_queue_depth=scheduler.backlog_depth(),
        retry_queue_depth=len(getattr(scheduler, "_retry_queue", [])),
        due_missions=due,
        persist_enabled=getattr(app.settings, "queue_persist_enabled", False),
    )
    dq = getattr(app, "distributed_queue", None)
    if dq:
        snap.lease_conflicts = dq.leases.metrics.get("lease_conflicts", 0)
        snap.stale_requeues = dq.leases.metrics.get("stale_requeued", 0)
    return snap


async def queue_snapshot_async(app: Any) -> QueueSnapshot:
    snap = queue_snapshot(app)
    dq = getattr(app, "distributed_queue", None)
    if dq:
        try:
            stats = await dq.stats()
            snap.durable_depth = int(stats.get("total", 0))
        except Exception:
            pass
    return snap


def worker_snapshot(app: Any) -> WorkerSnapshot:
    dispatcher = getattr(app, "mission_dispatcher", None)
    settings = app.settings
    mode = "dispatcher" if settings.mission_dispatch_enabled else "legacy_worker"
    if not settings.mission_dispatch_enabled and not settings.mission_worker_enabled:
        mode = "idle"
    dm = dispatcher.metrics if dispatcher else {}
    snap = WorkerSnapshot(
        dispatcher_running=bool(dm.get("heartbeat")),
        dispatcher_ticks=int(dm.get("ticks", 0)),
        dispatcher_executions=int(dm.get("executions", 0)),
        worker_mode=mode,
        last_tick_at=dm.get("last_tick_at"),
    )
    dq = getattr(app, "distributed_queue", None)
    if dq:
        snap.worker_id = dq.worker_id
    return snap


async def worker_snapshot_async(app: Any) -> WorkerSnapshot:
    snap = worker_snapshot(app)
    reg = getattr(app, "worker_registry", None)
    if reg:
        try:
            snap.runtime_workers = await reg.list_workers()
        except Exception:
            pass
    return snap


def detect_bottlenecks(app: Any) -> list[BottleneckReport]:
    reports: list[BottleneckReport] = []
    for mission in list(app.mission_manager._active.values()):  # noqa: SLF001
        st = migrate_legacy_state(mission.current_state)
        pending = sum(
            1
            for n in mission.task_graph.nodes.values()
            if n.status in (TaskNodeStatus.PENDING, TaskNodeStatus.READY)
        )
        blocked = sum(1 for n in mission.task_graph.nodes.values() if n.status == TaskNodeStatus.BLOCKED)
        ready = len(mission.task_graph.ready_nodes())

        reason = ""
        if st == MissionLifecycle.APPROVAL_REQUIRED:
            reason = "policy_approval_required"
        elif st == MissionLifecycle.ESCALATED:
            reason = "escalated_awaiting_human"
        elif pending > 0 and ready == 0 and blocked == 0:
            reason = "dependency_wait"
        elif blocked > 0:
            reason = "tasks_blocked"
        elif pending > 0 and ready > 0 and st in (
            MissionLifecycle.PLANNED,
            MissionLifecycle.DISPATCHED,
            MissionLifecycle.RUNNING,
        ):
            reason = "dispatcher_backlog"

        if reason:
            reports.append(
                BottleneckReport(
                    mission_id=mission.mission_id,
                    reason=reason,
                    pending_tasks=pending,
                    blocked_tasks=blocked,
                    state=st.value,
                )
            )
    return reports

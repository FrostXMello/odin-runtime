"""Execution dispatcher — task pickup, wave execution, stuck detection."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any

from odin_backend.core.missions.lifecycle import (
    DISPATCHABLE_MISSION_STATES,
    migrate_legacy_state,
    MissionStateMachine,
    TERMINAL_MISSION_STATES,
)
from odin_backend.models.mission import MissionLifecycle
from odin_backend.models.task_graph import TaskNodeStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ExecutionDispatcher:
    """
    Drives mission waves to completion.

    Separate from MissionWorkerPool loop scheduling — handles execution semantics.
    """

    def __init__(self, app: Any) -> None:
        self._app = app
        self._task: asyncio.Task | None = None
        self._running = False
        self._last_tick_at: float | None = None
        self._pickup_latencies: list[float] = []
        self._ticks = 0
        self._executions = 0
        self._stuck_requeued = 0
        self._wake_event = asyncio.Event()
        self._dependency_releases = 0
        self._async_dispatches = 0

    @property
    def metrics(self) -> dict[str, Any]:
        avg_pickup = sum(self._pickup_latencies[-50:]) / max(1, len(self._pickup_latencies[-50:]))
        async_m = getattr(self._app, "async_mission_runtime", None)
        async_metrics = async_m.metrics if async_m else {}
        dq = getattr(self._app, "distributed_queue", None)
        queue_metrics = dq.metrics if dq else {}
        lease_metrics = dq.leases.metrics if dq else {}
        return {
            "ticks": self._ticks,
            "executions": self._executions,
            "queue_depth": self._app.mission_worker.scheduler.backlog_depth(),
            "avg_pickup_latency_ms": round(avg_pickup * 1000, 2),
            "worker_utilization": min(1.0, self._executions / max(1, self._ticks)),
            "stuck_requeued": self._stuck_requeued,
            "last_tick_at": self._last_tick_at,
            "heartbeat": self._running,
            "wakeups": async_metrics.get("wakeups", 0),
            "async_dispatches": self._async_dispatches,
            "dependency_release_rate": self._dependency_releases,
            "execution_concurrency": async_metrics.get("active_futures", 0),
            "async_runtime": async_metrics,
            "queue_metrics": queue_metrics,
            "lease_conflicts": lease_metrics.get("lease_conflicts", 0),
            "stale_requeues": lease_metrics.get("stale_requeued", 0),
        }

    def wake(self, mission_id: str, *, reason: str = "runtime_event") -> None:
        """Signal dispatcher to process ready tasks without waiting for poll interval."""
        self._wake_event.set()
        q = getattr(self._app, "distributed_queue", None)
        if q and self._app.settings.queue_persist_enabled:
            import asyncio

            try:
                loop = asyncio.get_running_loop()
                loop.create_task(q.idempotent_wake(mission_id, reason=reason))
            except RuntimeError:
                self.enqueue(mission_id, delay=0.0)
        else:
            self.enqueue(mission_id, delay=0.0)
        obs = getattr(self._app, "observability", None)
        if obs:
            from odin_backend.core.observability.events import TraceEventKind

            obs.tracer.record(
                TraceEventKind.MISSION_RESUMED,
                message=reason,
                payload={"mission_id": mission_id},
                component="dispatcher",
            )

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("execution_dispatcher_started")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def enqueue(self, mission_id: str, *, delay: float = 0.0) -> None:
        self._app.mission_worker.scheduler.schedule(mission_id, delay_seconds=delay)

    async def dispatch_mission_now(self, mission_id: str) -> dict[str, Any]:
        """Immediate single-mission dispatch (API / tests)."""
        t0 = time.monotonic()
        manager = self._app.mission_manager
        mission = await manager.get(mission_id)
        if not mission:
            return {"error": "not_found"}
        result = await self._dispatch_one(mission)
        self._pickup_latencies.append(time.monotonic() - t0)
        self._executions += 1
        return result

    async def _loop(self) -> None:
        interval = self._app.settings.mission_dispatch_interval_seconds
        while self._running:
            try:
                try:
                    await asyncio.wait_for(self._wake_event.wait(), timeout=interval)
                    self._wake_event.clear()
                except asyncio.TimeoutError:
                    pass
                await self._tick()
            except Exception as exc:
                logger.exception("dispatcher_tick_error", error=str(exc))

    async def _tick(self) -> None:
        self._ticks += 1
        self._last_tick_at = time.monotonic()
        manager = self._app.mission_manager
        runtime = self._app.mission_runtime

        await self._detect_stuck_tasks()

        sched = self._app.mission_worker.scheduler
        if hasattr(sched, "pop_due_async"):
            due = await sched.pop_due_async()
        else:
            due = sched.pop_due()
        if not due:
            for mission in await manager.list_active_missions():
                st = migrate_legacy_state(mission.current_state)
                if st in DISPATCHABLE_MISSION_STATES:
                    self.enqueue(mission.mission_id, delay=0.0)
            return

        sem = asyncio.Semaphore(self._app.settings.mission_max_concurrent_missions)
        await asyncio.gather(
            *[self._dispatch_with_sem(runtime, manager, mid, sem) for mid in due[:10]],
            return_exceptions=True,
        )

    async def _dispatch_with_sem(self, runtime, manager, mission_id: str, sem: asyncio.Semaphore) -> None:
        async with sem:
            t0 = time.monotonic()
            mission = await manager.get(mission_id)
            if not mission:
                return
            await self._dispatch_one(mission, runtime=runtime)
            self._pickup_latencies.append(time.monotonic() - t0)
            self._executions += 1
            sched = self._app.mission_worker.scheduler
            if hasattr(sched, "ack_dispatched"):
                await sched.ack_dispatched(mission_id)

    async def _dispatch_one(self, mission: Any, *, runtime: Any | None = None) -> dict[str, Any]:
        runtime = runtime or self._app.mission_runtime
        sm = MissionStateMachine(mission)
        state = sm.state

        if state in TERMINAL_MISSION_STATES:
            return {"skipped": True, "state": state.value}

        if state == MissionLifecycle.APPROVAL_REQUIRED:
            return {"skipped": True, "state": "approval_required"}

        if state == MissionLifecycle.QUEUED:
            sm.transition(MissionLifecycle.PLANNING, reason="dispatcher")
        if sm.state == MissionLifecycle.PLANNING:
            self._app.mission_planner.plan(mission)
            sm.transition(MissionLifecycle.PLANNED, reason="dispatcher_planned")
        if sm.state == MissionLifecycle.PLANNED:
            sm.transition(MissionLifecycle.DISPATCHED, reason="dispatcher")
        if sm.state == MissionLifecycle.DISPATCHED:
            sm.transition(MissionLifecycle.RUNNING, reason="dispatcher")

        obs = getattr(self._app, "observability", None)
        if obs:
            from odin_backend.core.observability.events import TraceEventKind

            obs.tracer.mission_context(mission.mission_id)
            obs.tracer.record(
                TraceEventKind.MISSION_DISPATCHED,
                message="wave dispatch",
                payload={"state": sm.state.value},
                component="dispatcher",
            )
            t0 = time.monotonic()
        else:
            t0 = None

        result = await runtime.run_wave(self._app, mission)

        if result.get("async"):
            self._async_dispatches += 1

        if obs and t0 is not None:
            obs.metrics.record_dispatcher_pickup(time.monotonic() - t0)

        st = migrate_legacy_state(mission.current_state)
        in_flight = 0
        if hasattr(self._app, "async_mission_runtime"):
            in_flight = self._app.async_mission_runtime.in_flight_count(mission.mission_id)
        if st in (MissionLifecycle.RUNNING, MissionLifecycle.RETRYING) and not mission.is_terminal():
            if in_flight == 0 and not result.get("async"):
                self.enqueue(
                    mission.mission_id,
                    delay=self._app.settings.mission_cooldown_seconds,
                )
            elif in_flight > 0 or result.get("async"):
                self.enqueue(mission.mission_id, delay=0.05)

        return result

    async def _detect_stuck_tasks(self) -> None:
        timeout = self._app.settings.mission_stuck_task_seconds
        now = datetime.now(timezone.utc)
        manager = self._app.mission_manager

        for mission in await manager.list_active_missions():
            for node in mission.task_graph.nodes.values():
                if node.status not in (TaskNodeStatus.EXECUTING, TaskNodeStatus.RUNNING, TaskNodeStatus.ASSIGNED):
                    continue
                started = node.output.get("executing_started_at")
                if not started:
                    continue
                try:
                    ts = datetime.fromisoformat(started.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if (now - ts).total_seconds() > timeout:
                    node.status = TaskNodeStatus.PENDING
                    node.output["stuck_requeued"] = True
                    self._stuck_requeued += 1
                    mission.append_history("stuck_task_requeued", {"task_id": node.id})
                    logger.warning(
                        "stuck_task_requeued",
                        mission_id=mission.mission_id,
                        task_id=node.id,
                    )
            await manager.persist(mission)

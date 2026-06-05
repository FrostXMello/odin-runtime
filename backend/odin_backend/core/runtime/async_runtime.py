"""Async mission runtime — non-blocking wave dispatch and completion-driven progression."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Awaitable

from odin_backend.core.execution.models import ExecutionRecord, ExecutionState
from odin_backend.core.observability.events import TraceEventKind
from odin_backend.core.runtime.execution_context import MissionTaskExecutionContext
from odin_backend.core.runtime.locks import MissionLockManager
from odin_backend.core.runtime.task_contracts import TaskContractType, parse_task_contract
from odin_backend.models.mission import Mission
from odin_backend.models.task_graph import TaskNode, TaskNodeStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_TERMINAL = {
    ExecutionState.COMPLETED,
    ExecutionState.FAILED,
    ExecutionState.CANCELLED,
    ExecutionState.TIMED_OUT,
}


@dataclass
class ExecutionFuture:
    execution_id: str
    mission_id: str
    task_id: str
    started_at: datetime
    timeout_at: datetime | None = None
    state: str = "submitted"
    retry_count: int = 0
    processed: bool = False
    callback_registered: bool = False


@dataclass
class MissionExecutionSession:
    mission_id: str
    in_flight: dict[str, ExecutionFuture] = field(default_factory=dict)

    @property
    def active_count(self) -> int:
        return len(self.in_flight)


class ExecutionFutureRegistry:
    def __init__(self) -> None:
        self._by_execution: dict[str, ExecutionFuture] = {}
        self._by_task: dict[tuple[str, str], str] = {}
        self._processed: set[str] = set()

    def register(self, fut: ExecutionFuture) -> None:
        self._by_execution[fut.execution_id] = fut
        self._by_task[(fut.mission_id, fut.task_id)] = fut.execution_id

    def get(self, execution_id: str) -> ExecutionFuture | None:
        return self._by_execution.get(execution_id)

    def get_by_task(self, mission_id: str, task_id: str) -> ExecutionFuture | None:
        eid = self._by_task.get((mission_id, task_id))
        return self._by_execution.get(eid) if eid else None

    def mark_processed(self, execution_id: str) -> bool:
        if execution_id in self._processed:
            return False
        self._processed.add(execution_id)
        fut = self._by_execution.get(execution_id)
        if fut:
            fut.processed = True
        return True

    def drop(self, execution_id: str) -> None:
        fut = self._by_execution.pop(execution_id, None)
        if fut:
            self._by_task.pop((fut.mission_id, fut.task_id), None)


class RuntimeCompletionBus:
    def __init__(self) -> None:
        self._handlers: list[Callable[[ExecutionRecord], Awaitable[None]]] = []

    def subscribe(self, handler: Callable[[ExecutionRecord], Awaitable[None]]) -> None:
        self._handlers.append(handler)

    async def publish(self, record: ExecutionRecord) -> None:
        for h in self._handlers:
            try:
                await h(record)
            except Exception as exc:
                logger.warning("completion_bus_handler_error", error=str(exc))


class AsyncMissionRuntimeCoordinator:
    """Event-driven mission task execution without blocking the dispatcher."""

    def __init__(self, app: Any) -> None:
        self._app = app
        self.registry = ExecutionFutureRegistry()
        self.sessions: dict[str, MissionExecutionSession] = {}
        self.completion_bus = RuntimeCompletionBus()
        self.locks = MissionLockManager()
        self._watchers: dict[str, asyncio.Task] = {}
        self._metrics: dict[str, Any] = {
            "submitted_async": 0,
            "callbacks_received": 0,
            "dependency_releases": 0,
            "duplicate_callbacks_suppressed": 0,
            "async_waves_dispatched": 0,
            "active_futures": 0,
            "wakeups": 0,
        }
        self.completion_bus.subscribe(self._on_completion_record)

    @property
    def metrics(self) -> dict[str, Any]:
        out = dict(self._metrics)
        out["active_futures"] = len(self.registry._by_execution)  # noqa: SLF001
        out["active_sessions"] = len(self.sessions)
        return out

    def session(self, mission_id: str) -> MissionExecutionSession:
        if mission_id not in self.sessions:
            self.sessions[mission_id] = MissionExecutionSession(mission_id=mission_id)
        return self.sessions[mission_id]

    async def submit_from_wave(
        self,
        app: Any,
        mission: Mission,
        task: TaskNode,
        *,
        runtime: Any,
    ) -> dict[str, Any]:
        """Submit task without waiting — returns immediately."""
        bridge = app.mission_execution_bridge
        bridge.planner.sync_dependencies(mission)
        bridge.planner.enrich_mission(mission)
        contract = parse_task_contract(task, mission_strategy=mission.execution_strategy)

        if contract.type == TaskContractType.NOOP:
            await self._complete_inline(app, mission, task, runtime, success=True)
            return {"task_id": task.id, "inline": True, "success": True}

        if contract.type == TaskContractType.TOOL:
            ok = await bridge._run_tool_pipeline(mission, task, contract.tool_name or "noop", contract.params)
            await self._complete_inline(app, mission, task, runtime, success=ok)
            return {"task_id": task.id, "inline": True, "success": ok}

        ok, reason = bridge.router.validate(contract)
        if not ok:
            task.output["execution_error"] = reason
            await self._complete_inline(app, mission, task, runtime, success=False)
            return {"task_id": task.id, "inline": True, "success": False}

        run_req = bridge.router.to_run_request(
            contract,
            mission_id=mission.mission_id,
            task_id=task.id,
            executor_agent=task.assigned_agent or "brokk",
            app=app,
        )
        if not run_req:
            await self._complete_inline(app, mission, task, runtime, success=True)
            return {"task_id": task.id, "inline": True, "success": True}

        obs = getattr(app, "observability", None)
        if obs:
            obs.tracer.link_task(mission.mission_id, task.id)
            obs.tracer.record(
                TraceEventKind.EXECUTION_SUBMITTED_ASYNC,
                message=task.goal[:80],
                payload={"capability": contract.capability},
                component="async_runtime",
            )

        record = await app.execution_engine.submit(run_req)
        bridge._task_to_execution[(mission.mission_id, task.id)] = record.execution_id
        bridge._execution_to_task[record.execution_id] = (mission.mission_id, task.id)
        task.output["execution_id"] = record.execution_id

        timeout_s = contract.timeout_seconds or app.settings.execution_default_timeout_seconds
        fut = ExecutionFuture(
            execution_id=record.execution_id,
            mission_id=mission.mission_id,
            task_id=task.id,
            started_at=datetime.now(timezone.utc),
            timeout_at=datetime.now(timezone.utc) + timedelta(seconds=timeout_s + 30),
            state=record.state.value,
        )
        self.registry.register(fut)
        self.session(mission.mission_id).in_flight[task.id] = fut
        self._metrics["submitted_async"] += 1

        mission.task_graph.update_status(task.id, TaskNodeStatus.RUNNING, reason="async_submit", strict=False)

        self._start_watcher(record.execution_id)
        return {"task_id": task.id, "execution_id": record.execution_id, "async": True}

    def _start_watcher(self, execution_id: str) -> None:
        if execution_id in self._watchers:
            return
        self._watchers[execution_id] = asyncio.create_task(self._watch_execution(execution_id))

    async def _watch_execution(self, execution_id: str) -> None:
        engine = self._app.execution_engine
        try:
            while True:
                rec = await engine.get(execution_id)
                if rec and rec.state in _TERMINAL:
                    await self.completion_bus.publish(rec)
                    break
                await asyncio.sleep(0.08)
        except asyncio.CancelledError:
            pass
        finally:
            self._watchers.pop(execution_id, None)

    async def _on_completion_record(self, record: ExecutionRecord) -> None:
        if not self.registry.mark_processed(record.execution_id):
            self._metrics["duplicate_callbacks_suppressed"] += 1
            return
        self._metrics["callbacks_received"] += 1
        fut = self.registry.get(record.execution_id)
        if not fut:
            return

        obs = getattr(self._app, "observability", None)
        if obs:
            obs.tracer.record(
                TraceEventKind.EXECUTION_CALLBACK_RECEIVED,
                message=record.state.value,
                payload={"execution_id": record.execution_id},
                component="async_runtime",
            )

        if record.state == ExecutionState.COMPLETED:
            await self.on_execution_completed(record)
        elif record.state == ExecutionState.CANCELLED:
            await self.on_execution_cancelled(record)
        elif record.state == ExecutionState.TIMED_OUT:
            await self.on_execution_timeout(record)
        else:
            await self.on_execution_failed(record)

    async def on_execution_completed(self, record: ExecutionRecord) -> None:
        await self._handle_terminal(record, success=True)

    async def on_execution_failed(self, record: ExecutionRecord) -> None:
        await self._handle_terminal(record, success=False)

    async def on_execution_cancelled(self, record: ExecutionRecord) -> None:
        await self._handle_terminal(record, success=False, cancelled=True)

    async def on_execution_timeout(self, record: ExecutionRecord) -> None:
        await self._handle_terminal(record, success=False, timed_out=True)

    async def _handle_terminal(
        self,
        record: ExecutionRecord,
        *,
        success: bool,
        cancelled: bool = False,
        timed_out: bool = False,
    ) -> None:
        mid = record.mission_id
        tid = record.task_id
        if not mid or not tid:
            mapping = self._app.mission_execution_bridge.get_mission_task(record.execution_id)
            if mapping:
                mid, tid = mapping
        if not mid or not tid:
            self.registry.drop(record.execution_id)
            return

        runtime = self._app.mission_runtime
        bridge = self._app.mission_execution_bridge

        async with self.locks.mission(mid):
            mission = await self._app.mission_manager.get(mid)
            if not mission:
                self.registry.drop(record.execution_id)
                return
            task = mission.task_graph.get(tid)
            if not task:
                self.registry.drop(record.execution_id)
                return

            contract = parse_task_contract(task, mission_strategy=mission.execution_strategy)
            ctx = MissionTaskExecutionContext(
                mission=mission,
                task=task,
                contract=contract,
                execution_id=record.execution_id,
            )
            hook = await bridge.hooks.on_execution_finished(self._app, ctx, record)
            exp = getattr(self._app, "experience_engine", None)
            intel = getattr(self._app, "execution_intelligence", None)
            if exp:
                await exp.record_outcome_async(
                    mission_id=mid,
                    task_id=tid,
                    execution_id=record.execution_id,
                    capability=record.capability_used,
                    tool=task.output.get("tool"),
                    success=success,
                    reason=record.state.value,
                )
            if intel:
                intel.record_execution(
                    record.capability_used,
                    success=success,
                    execution_id=record.execution_id,
                )
                obs = getattr(self._app, "observability", None)
                if obs:
                    from odin_backend.core.observability.events import TraceEventKind

                    obs.tracer.record(
                        TraceEventKind.EXECUTION_PROFILE_UPDATED,
                        message="execution profile updated",
                        payload={"execution_id": record.execution_id, "capability": record.capability_used},
                        component="execution_intelligence",
                    )
            if hook.get("dependents_released"):
                released = len(hook["dependents_released"])
                self._metrics["dependency_releases"] += released
                disp = getattr(self._app, "mission_dispatcher", None)
                if disp and hasattr(disp, "_dependency_releases"):
                    disp._dependency_releases += released

            sess = self.session(mid)
            sess.in_flight.pop(tid, None)
            self.registry.drop(record.execution_id)

            obs = getattr(self._app, "observability", None)
            if success:
                mission.task_graph.update_status(
                    tid,
                    TaskNodeStatus.COMPLETE,
                    output={"completed": True},
                    reason="async_execution_success",
                    strict=False,
                )
                runtime._metrics["tasks_completed"] += 1
                if obs:
                    obs.tracer.record(
                        TraceEventKind.TASK_COMPLETED,
                        message=task.goal[:80],
                        component="async_runtime",
                    )
                await runtime._memory.link_task_completion(mid, tid, task.goal)
                await runtime._post_feedback(self._app, mission, task, True, "")
            else:
                if obs:
                    obs.tracer.record(
                        TraceEventKind.TASK_FAILED,
                        message=task.goal[:80],
                        component="async_runtime",
                    )
                handled = False
                if hasattr(self._app, "mission_execution_adaptive"):
                    decision = self._app.mission_execution_adaptive.decide(
                        self._app,
                        mission,
                        task,
                        execution_state=record.state.value,
                        contract_blocking=contract.blocking,
                    )
                    applied = await self._app.mission_execution_adaptive.apply_decision_async(
                        self._app,
                        mission,
                        task,
                        decision,
                        runtime=runtime,
                    )
                    if applied.get("action") == "retry":
                        self._schedule_mission_wake(mid, delay=applied.get("delay", 0.5))
                        await self._app.mission_manager.persist(mission)
                        return
                    if applied.get("action") == "isolate_branch":
                        success = True
                        handled = True
                        mission.task_graph.update_status(
                            tid, TaskNodeStatus.SKIPPED, reason="isolated", strict=False
                        )
                if not success and not handled:
                    adapted = await runtime._handle_task_failure(self._app, mission, task)
                    if adapted.get("recovered"):
                        runtime._metrics["recoveries"] += 1
                await runtime._post_feedback(
                    self._app, mission, task, success, "" if success else record.state.value
                )

            mission.append_history(
                "task_executed_async",
                {
                    "task_id": tid,
                    "execution_id": record.execution_id,
                    "success": success,
                    "state": record.state.value,
                    "cancelled": cancelled,
                    "timed_out": timed_out,
                },
            )
            await self._app.mission_manager.persist(mission)
            await runtime._evaluate_completion(self._app, mission)
            self._wake_dispatcher(mid)

    async def _complete_inline(
        self,
        app: Any,
        mission: Mission,
        task: TaskNode,
        runtime: Any,
        *,
        success: bool,
    ) -> None:
        async with self.locks.mission(mission.mission_id):
            if success:
                mission.task_graph.update_status(
                    task.id, TaskNodeStatus.COMPLETE, reason="inline_async"
                )
                runtime._metrics["tasks_completed"] += 1
            else:
                await runtime._handle_task_failure(app, mission, task)
            await app.mission_manager.persist(mission)
            await runtime._evaluate_completion(app, mission)
        self._wake_dispatcher(mission.mission_id)

    def _wake_dispatcher(self, mission_id: str) -> None:
        self._metrics["wakeups"] += 1
        disp = getattr(self._app, "mission_dispatcher", None)
        if disp and hasattr(disp, "wake"):
            disp.wake(mission_id)
        else:
            self._app.mission_worker.enqueue_mission(mission_id)

    def _schedule_mission_wake(self, mission_id: str, *, delay: float) -> None:
        async def _delayed():
            await asyncio.sleep(delay)
            self._wake_dispatcher(mission_id)

        asyncio.create_task(_delayed())

    def in_flight_count(self, mission_id: str) -> int:
        return self.session(mission_id).active_count

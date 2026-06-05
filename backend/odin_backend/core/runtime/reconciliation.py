"""Startup reconciliation for in-flight async executions."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.core.execution.models import ExecutionState
from odin_backend.core.observability.events import TraceEventKind
from odin_backend.models.task_graph import TaskNodeStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_ACTIVE = {
    ExecutionState.QUEUED,
    ExecutionState.ALLOCATED,
    ExecutionState.RUNNING,
    ExecutionState.RETRYING,
    ExecutionState.WAITING,
}


class ExecutionReconciliationService:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._metrics: dict[str, int] = {
            "reconciled_executions": 0,
            "orphan_tasks_repaired": 0,
            "watchers_restored": 0,
        }

    @property
    def metrics(self) -> dict[str, Any]:
        return dict(self._metrics)

    async def reconcile_on_startup(self) -> dict[str, Any]:
        engine = self._app.execution_engine
        coordinator = getattr(self._app, "async_mission_runtime", None)
        if not coordinator:
            return {"skipped": True}

        records = await engine.store.list_all(limit=500)
        active = [r for r in records if r.state in _ACTIVE and r.mission_id]

        obs = getattr(self._app, "observability", None)
        for rec in active:
            async with coordinator.locks.reconciliation(rec.mission_id):
                from odin_backend.core.runtime.async_runtime import ExecutionFuture

                fut = ExecutionFuture(
                    execution_id=rec.execution_id,
                    mission_id=rec.mission_id or "",
                    task_id=rec.task_id or "",
                    started_at=rec.started_at or rec.created_at,
                    state=rec.state.value,
                )
                coordinator.registry.register(fut)
                if rec.mission_id and rec.task_id:
                    coordinator.session(rec.mission_id).in_flight[rec.task_id] = fut
                    bridge = self._app.mission_execution_bridge
                    bridge._task_to_execution[(rec.mission_id, rec.task_id)] = rec.execution_id
                    bridge._execution_to_task[rec.execution_id] = (rec.mission_id, rec.task_id)
                coordinator._start_watcher(rec.execution_id)
                self._metrics["watchers_restored"] += 1
                self._metrics["reconciled_executions"] += 1

                if obs:
                    obs.tracer.record(
                        TraceEventKind.GRAPH_RECONCILED,
                        message="execution watcher restored",
                        payload={"execution_id": rec.execution_id},
                        component="reconciliation",
                    )

        await self._repair_orphan_tasks()
        return {"reconciled": self._metrics["reconciled_executions"], **self._metrics}

    async def _repair_orphan_tasks(self) -> None:
        manager = self._app.mission_manager
        for mission in await manager.list_active_missions():
            repaired = False
            for node in mission.task_graph.nodes.values():
                if node.status not in (TaskNodeStatus.EXECUTING, TaskNodeStatus.RUNNING):
                    continue
                eid = node.output.get("execution_id")
                if eid:
                    rec = await self._app.execution_engine.get(eid)
                    if rec and rec.state in _ACTIVE:
                        continue
                node.status = TaskNodeStatus.PENDING
                node.output["orphan_repaired"] = True
                repaired = True
                self._metrics["orphan_tasks_repaired"] += 1
            if repaired:
                mission.append_history("orphan_tasks_repaired", {})
                await manager.persist(mission)
                if hasattr(self._app, "async_mission_runtime"):
                    self._app.async_mission_runtime._wake_dispatcher(mission.mission_id)

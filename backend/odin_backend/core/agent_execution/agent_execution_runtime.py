"""Agent task execution orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agent_execution.autonomous_tasks import AutonomousTaskStore
from odin_backend.core.agent_execution.cooperative_runtime import CooperativeRuntime
from odin_backend.core.agent_execution.delegated_execution import DelegatedExecution
from odin_backend.core.agent_execution.execution_memory import ExecutionMemory
from odin_backend.core.agent_execution.objective_scheduler import ObjectiveScheduler
from odin_backend.core.agent_execution.recursive_subtasks import decompose
from odin_backend.core.agent_execution.task_negotiation import negotiate


class AgentExecutionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._store = AutonomousTaskStore(app.settings)
        self._delegation = DelegatedExecution()
        self._coop = CooperativeRuntime()
        self._scheduler = ObjectiveScheduler()
        self._memory = ExecutionMemory()

    async def connect(self) -> None:
        await self._store.connect()

    async def disconnect(self) -> None:
        await self._store.disconnect()

    async def spawn_task(self, *, owner_agent_id: str, title: str, mission_id: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "agent_execution_enabled", False):
            return {"accepted": False, "reason": "agent_execution_disabled"}
        subtasks = decompose(title)
        task = await self._store.create(owner_agent_id=owner_agent_id, title=title, mission_id=mission_id, payload={"subtasks": subtasks})
        self._scheduler.enqueue(task_id=task["task_id"])
        self._delegation.lease(task_id=task["task_id"], agent_id=owner_agent_id)
        self._emit("task_delegated", task)
        return {"accepted": True, "task": task, "subtasks": subtasks}

    async def negotiate_ownership(self, *, agent_ids: list[str], task_title: str) -> dict[str, Any]:
        agents = [{"agent_id": a, "confidence": 0.6} for a in agent_ids]
        return negotiate(agents, task_title)

    async def resume_pending(self) -> list[dict[str, Any]]:
        pending = await self._store.list_pending()
        for p in pending:
            self._memory.record(task_id=p["task_id"], outcome="resumed")
        return pending

    def snapshot(self) -> dict[str, Any]:
        return {"scheduler_queue": len(self._scheduler._queue), "collaborations": len(self._coop._collaborations)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="agent_execution")

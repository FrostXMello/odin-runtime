"""Execution coordination orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.execution_coordination.cooperative_execution import coordinate_agents
from odin_backend.core.execution_coordination.execution_attention import focus_execution
from odin_backend.core.execution_coordination.execution_supervisor import supervise
from odin_backend.core.execution_coordination.operator_intervention import intervention_checkpoint
from odin_backend.core.execution_coordination.recovery_coordination import recover_partial
from odin_backend.core.execution_coordination.task_orchestrator import orchestrate
from odin_backend.core.execution_coordination.workflow_state_machine import WorkflowState


class ExecutionCoordinationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._workflows: dict[str, WorkflowState] = {}

    async def start_workflow(self, *, workflow_id: str, steps: list[str]) -> dict[str, Any]:
        if not getattr(self._app.settings, "execution_coordination_enabled", False):
            return {"accepted": False, "reason": "execution_coordination_disabled"}
        wf = WorkflowState(workflow_id=workflow_id, steps=steps)
        self._workflows[workflow_id] = wf
        plan = orchestrate(steps=steps)
        supervision = supervise(workflow_id=workflow_id, step=steps[0] if steps else "")
        self._emit("execution_supervised", supervision)
        return {"accepted": True, "workflow_id": workflow_id, "plan": plan, "supervision": supervision, "approval_required": True}

    async def pause(self, *, workflow_id: str) -> dict[str, Any]:
        wf = self._workflows.get(workflow_id)
        if not wf:
            return {"accepted": False, "reason": "workflow_not_found"}
        wf.pause()
        return {"accepted": True, "paused": True}

    async def resume(self, *, workflow_id: str, approved: bool = False) -> dict[str, Any]:
        wf = self._workflows.get(workflow_id)
        if not wf:
            return {"accepted": False, "reason": "workflow_not_found"}
        checkpoint = intervention_checkpoint(approved=approved)
        if not checkpoint["allowed"]:
            return {"accepted": False, "reason": "approval_required"}
        wf.resume()
        recovery = recover_partial(workflow_id=workflow_id, completed=wf.completed_steps())
        return {"accepted": True, "resumed": True, "recovery": recovery}

    async def coordinate(self, *, agents: list[str], task: str) -> dict[str, Any]:
        return {"accepted": True, **coordinate_agents(agents=agents, task=task), **focus_execution(task=task)}

    def snapshot(self) -> dict[str, Any]:
        return {"workflows": len(self._workflows)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="execution_coordination")

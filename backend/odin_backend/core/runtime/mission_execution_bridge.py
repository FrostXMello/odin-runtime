"""Mission ↔ Execution bridge — real work for mission tasks."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.core.execution.models import ExecutionState
from odin_backend.core.runtime.completion_hooks import ExecutionCompletionHooks
from odin_backend.core.runtime.execution_context import MissionTaskExecutionContext
from odin_backend.core.runtime.execution_planner import MissionExecutionPlanner
from odin_backend.core.runtime.task_contracts import TaskContractType, parse_task_contract
from odin_backend.core.runtime.task_router import TaskRouter
from odin_backend.models.mission import Mission
from odin_backend.models.task_graph import TaskNode
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_TERMINAL = {
    ExecutionState.COMPLETED,
    ExecutionState.FAILED,
    ExecutionState.CANCELLED,
    ExecutionState.TIMED_OUT,
}


class MissionExecutionBridge:
    def __init__(self, app: Any) -> None:
        self._app = app
        self.router = TaskRouter()
        self.planner = MissionExecutionPlanner()
        self.hooks = ExecutionCompletionHooks(self)
        self._task_to_execution: dict[tuple[str, str], str] = {}
        self._execution_to_task: dict[str, tuple[str, str]] = {}

    def get_execution_id(self, mission_id: str, task_id: str) -> str | None:
        return self._task_to_execution.get((mission_id, task_id))

    def get_mission_task(self, execution_id: str) -> tuple[str, str] | None:
        return self._execution_to_task.get(execution_id)

    async def list_mission_executions(self, mission_id: str) -> list[dict]:
        records = await self._app.execution_engine.store.list_by_mission(mission_id)
        return [r.model_dump(mode="json") for r in records]

    async def execute_task(self, mission: Mission, task: TaskNode) -> bool:
        """Run task via execution engine or fall back to tool pipeline."""
        self.planner.sync_dependencies(mission)
        self.planner.enrich_mission(mission)

        contract = parse_task_contract(task, mission_strategy=mission.execution_strategy)
        if mission.execution_strategy == "conservative_readonly":
            mission.append_history("task_noop_complete", {"task_id": task.id, "strategy": "conservative_readonly"})
            return True

        ok, reason = self.router.validate(contract)
        if not ok:
            task.output["execution_error"] = reason
            logger.warning("task_contract_invalid", task_id=task.id, reason=reason)
            return False

        if contract.type == TaskContractType.NOOP:
            mission.append_history("task_noop_complete", {"task_id": task.id})
            return True

        if contract.type == TaskContractType.TOOL:
            return await self._run_tool_pipeline(mission, task, contract.tool_name or "noop", contract.params)

        if not getattr(self._app.settings, "execution_engine_enabled", True):
            return await self._run_tool_pipeline(mission, task, contract.tool_name or "noop", contract.params)

        run_req = self.router.to_run_request(
            contract,
            mission_id=mission.mission_id,
            task_id=task.id,
            executor_agent=task.assigned_agent or "brokk",
            app=self._app,
        )
        if not run_req:
            return True

        obs = getattr(self._app, "observability", None)
        if obs:
            obs.tracer.link_task(mission.mission_id, task.id)

        record = await self._app.execution_engine.submit(run_req)
        self._task_to_execution[(mission.mission_id, task.id)] = record.execution_id
        self._execution_to_task[record.execution_id] = (mission.mission_id, task.id)
        task.output["execution_id"] = record.execution_id

        ctx = MissionTaskExecutionContext(
            mission=mission,
            task=task,
            contract=contract,
            execution_id=record.execution_id,
        )

        timeout = (contract.timeout_seconds or self._app.settings.execution_default_timeout_seconds) + 30
        final = await self._app.execution_engine.wait_for(record.execution_id, timeout=timeout)
        if not final:
            await self._app.execution_engine.cancel(record.execution_id, reason="wait_timeout")
            final = await self._app.execution_engine.get(record.execution_id)

        hook_result = await self.hooks.on_execution_finished(self._app, ctx, final)
        success = hook_result.get("success", False)

        if not success and hasattr(self._app, "mission_execution_adaptive"):
            decision = self._app.mission_execution_adaptive.decide(
                self._app,
                mission,
                task,
                execution_state=final.state.value,
                contract_blocking=contract.blocking,
            )
            applied = await self._app.mission_execution_adaptive.apply_decision(
                self._app,
                mission,
                task,
                decision,
                runtime=self._app.mission_runtime,
            )
            if applied.get("action") == "retry":
                return False
            if applied.get("action") == "isolate_branch":
                return True

        mission.append_history(
            "task_executed",
            {
                "task_id": task.id,
                "execution_id": record.execution_id,
                "success": success,
                "state": final.state.value,
            },
        )
        return success

    async def cancel_mission_executions(self, mission_id: str, *, reason: str = "mission_cancel") -> int:
        n = 0
        for (mid, tid), eid in list(self._task_to_execution.items()):
            if mid != mission_id:
                continue
            await self._app.execution_engine.cancel(eid, reason=reason)
            n += 1
        return n

    async def _run_tool_pipeline(
        self,
        mission: Mission,
        task: TaskNode,
        tool: str,
        params: dict,
    ) -> bool:
        from odin_backend.core.governor.decisions import ExecutionRequest

        request = ExecutionRequest(
            tool_name=tool,
            agent_id=task.assigned_agent or "odin",
            params=params,
            workflow_id=mission.mission_id,
            task_id=task.id,
            user_confirmed=mission.human_approved,
        )
        gate = self._app.adaptive_policy if hasattr(self._app, "adaptive_policy") else self._app.execution_gate
        if hasattr(gate, "validate"):
            from odin_backend.core.execution_gate.gate import GateDecision

            gate_result = gate.validate(self._app, request)
            if gate_result.decision != GateDecision.ALLOW:
                return False
        result = await self._app.execution_contract.run_tool_pipeline(
            self._app, request, skip_stability=True
        )
        return result.success

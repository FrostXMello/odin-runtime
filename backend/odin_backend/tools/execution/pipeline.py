"""VALKYRIE live tool execution — Kernel → Governor → Gate → Heimdall → Tool."""

from typing import Any
from uuid import uuid4

from odin_backend.core.execution_gate.gate import GateDecision
from odin_backend.core.governor.decisions import ExecutionRequest, GovernorDecisionType
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class LiveToolPipeline:
    """
    Enforced chain:
    Governor → ExecutionGate → Heimdall (executor) → Tool → Memory event
    """

    async def execute_with_trace(
        self,
        app: Any,
        tool_name: str,
        params: dict,
        *,
        agent_id: str = "valkyrie",
        task_id: str | None = None,
        user_confirmed: bool = False,
        execution_trace_id: str | None = None,
        category: str = "live",
    ) -> dict[str, Any]:
        trace_id = execution_trace_id or str(uuid4())
        request = ExecutionRequest(
            tool_name=tool_name,
            agent_id=agent_id,
            params=params,
            task_id=task_id,
            user_confirmed=user_confirmed,
        )

        gate = app.execution_gate.validate(app, request)
        if gate.decision != GateDecision.ALLOW:
            return {
                "success": False,
                "execution_trace_id": trace_id,
                "gate_decision": gate.decision.value,
                "governor_decision": "not_reached",
                "heimdall_check_result": "blocked_at_gate",
                "tool_output": {"reason": gate.reason},
                "environment_snapshot": app.env_config.snapshot(),
                "valkyrie_trace": [f"gate:{gate.decision.value}"],
            }

        result = await app.execution_contract.run_tool_pipeline(app, request, skip_stability=True)
        governor_decision = result.decision.value if hasattr(result.decision, "value") else str(result.decision)

        heimdall_result = "approved" if result.success else "denied_or_failed"
        tool_output = result.output if result.success else {"errors": result.reason}

        if result.success:
            try:
                mem_id = await app.memory.save_memory(
                    f"[{category}] Tool {tool_name} via VALKYRIE pipeline",
                    category="outcome",
                    metadata={
                        "tool": tool_name,
                        "trace_id": trace_id,
                        "governor": governor_decision,
                        "gate": gate.decision.value,
                    },
                )
                await self._emit_memory_event(app, tool_name, mem_id)
            except Exception as exc:
                logger.warning("live_tool_memory_skip", error=str(exc))

        app.kernel._state.environment_snapshot = app.env_config.snapshot()
        app.kernel._record_live_mind(
            decision_path=["governor", governor_decision, "gate", gate.decision.value, "valkyrie"],
        )

        return {
            "success": result.success,
            "execution_trace_id": trace_id,
            "governor_decision": governor_decision,
            "gate_decision": gate.decision.value,
            "heimdall_check_result": heimdall_result,
            "tool_output": tool_output,
            "environment_snapshot": app.env_config.snapshot(),
            "pipeline_trace": result.trace,
            "valkyrie_trace": ["governor", "gate", "heimdall", "tool"],
        }

    async def execute(
        self,
        app: Any,
        tool_name: str,
        params: dict,
        *,
        agent_id: str = "odin",
        task_id: str | None = None,
        user_confirmed: bool = False,
    ) -> dict[str, Any]:
        return await self.execute_with_trace(
            app,
            tool_name,
            params,
            agent_id=agent_id,
            task_id=task_id,
            user_confirmed=user_confirmed,
        )

    async def chain(
        self,
        app: Any,
        steps: list[dict[str, Any]],
        *,
        agent_id: str = "valkyrie",
    ) -> list[dict[str, Any]]:
        outputs: list[dict[str, Any]] = []
        for step in steps:
            tool = step.get("tool")
            if not tool:
                continue
            params = dict(step.get("params", {}))
            if outputs and step.get("use_previous"):
                params["previous"] = outputs[-1].get("tool_output", {})
            out = await self.execute_with_trace(
                app,
                tool,
                params,
                agent_id=agent_id,
                task_id=step.get("task_id"),
                user_confirmed=step.get("user_confirmed", False),
            )
            outputs.append(out)
            if not out.get("success"):
                break
        return outputs

    async def _emit_memory_event(self, app: Any, tool_name: str, memory_id: str) -> None:
        from odin_backend.core.bus.unified_bus import SignalUnificationBus

        event = Event(
            type=EventType.MEMORY_UPDATED,
            source=AgentId.VALKYRIE,
            payload={"tool": tool_name, "memory_id": memory_id, "via": "live_pipeline"},
        )
        bus = app.event_bus
        if isinstance(bus, SignalUnificationBus):
            await bus.inner.publish(event)
        else:
            await bus.publish(event)

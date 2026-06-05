"""Execution contract — no silent execution; full pipeline trace."""

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.governor.decisions import (
    ExecutionRequest,
    GovernorDecision,
    GovernorDecisionType,
)
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class PipelineResult(BaseModel):
    success: bool
    decision: GovernorDecisionType
    reason: str
    trace: list[dict[str, Any]] = Field(default_factory=list)
    output: dict[str, Any] = Field(default_factory=dict)


class ExecutionContract:
    """
    Mandatory execution pipeline:

    1. Task created
    2. Coherence validated
    3. Governor approves
    4. Autonomy checked
    5. Agent assigned (if applicable)
    6. Execution
    7. Result validated
    8. Memory updated
    9. Stability audit triggered (signal only)
    """

    async def run_tool_pipeline(
        self,
        app: Any,
        request: ExecutionRequest,
        *,
        skip_stability: bool = False,
    ) -> PipelineResult:
        trace: list[dict[str, Any]] = []
        kernel = app.kernel
        state = kernel.get_state()

        def log_step(step: str, detail: dict) -> None:
            trace.append({"step": step, **detail})
            state.append_execution_step(step, detail)

        # 1 — task context
        task_id = request.workflow_id or request.tool_name
        log_step("task_context", {"task_id": task_id, "tool": request.tool_name})

        # 2 — coherence
        report = app.coherence.validate(state, kernel.recent_signals(30))
        state.apply_coherence(report)
        log_step("coherence", {"score": report.coherence_score, "conflicts": len(report.conflict_report)})

        if report.conflict_report and app.coherence.blocks_execution():
            decision = GovernorDecision(
                decision=GovernorDecisionType.ESCALATE_TO_USER,
                reason="Coherence conflicts — resolve before execution",
                explainable={"conflicts": report.conflict_report},
                remediation="; ".join(report.resolution_suggestions[:2]),
            )
            kernel.commit_state(state)
            await self._emit_step(app, "coherence_escalate", decision.model_dump())
            return PipelineResult(
                success=False,
                decision=GovernorDecisionType.ESCALATE_TO_USER,
                reason=decision.reason,
                trace=trace,
            )

        # 3–4 — governor (includes autonomy)
        decision = await app.governor.evaluate(request, cognitive_state=state)
        log_step("governor", {"decision": decision.decision.value, "reason": decision.reason})

        if decision.decision not in (GovernorDecisionType.APPROVE,):
            kernel.commit_state(state)
            await self._emit_step(app, "governor_blocked", decision.model_dump())
            return PipelineResult(
                success=False,
                decision=decision.decision,
                reason=decision.reason,
                trace=trace,
            )

        # 5 — agent assignment trace
        log_step("agent_assignment", {"agent": request.agent_id, "tool": request.tool_name})

        # 6 — execution via runtime executor (governor already passed)
        from odin_backend.tools.base import ToolContext

        try:
            agent = AgentId(request.agent_id)
        except ValueError:
            agent = AgentId.ODIN
        ctx = ToolContext(
            agent_id=agent,
            correlation_id=request.workflow_id,
            task_id=request.task_id,
            user_confirmed=request.user_confirmed,
        )

        result = await app.tool_executor.execute(
            request.tool_name,
            request.params,
            ctx,
            skip_governor=True,
        )
        log_step(
            "execution",
            {"success": result.success, "errors": result.errors},
        )

        # 7 — validate result
        if not result.success:
            kernel.commit_state(state)
            return PipelineResult(
                success=False,
                decision=GovernorDecisionType.DENY,
                reason="; ".join(result.errors) or "execution_failed",
                trace=trace,
                output=result.data,
            )

        # 8 — memory update
        try:
            await app.memory.save_memory(
                f"Tool {request.tool_name} executed by {request.agent_id}",
                category="outcome",
                metadata={"tool": request.tool_name, "trace_id": result.trace_id},
            )
            log_step("memory_updated", {"tool": request.tool_name})
        except Exception as exc:
            log_step("memory_skipped", {"error": str(exc)})

        # 9 — stability audit (corrective signals only; conscious loop runs on interval)
        if app.settings.stability_loop_enabled and not skip_stability:
            audit = await app.stability.run_cycle(app)
            kernel.record_stability_check(audit)
            log_step("stability_audit", {"coherence_score": audit.get("coherence_score")})

        kernel.commit_state(state)
        await self._emit_step(app, "pipeline_complete", {"tool": request.tool_name})

        return PipelineResult(
            success=True,
            decision=GovernorDecisionType.APPROVE,
            reason="Pipeline complete",
            trace=trace,
            output=result.data,
        )

    async def _emit_step(self, app: Any, step: str, payload: dict) -> None:
        from odin_backend.core.bus.unified_bus import SignalUnificationBus

        event = Event(
            type=EventType.EXECUTION_PIPELINE_STEP,
            source=AgentId.ODIN,
            payload={"step": step, **payload},
        )
        bus = app.event_bus
        if isinstance(bus, SignalUnificationBus):
            await bus.inner.publish(event)
        else:
            await bus.publish(event)

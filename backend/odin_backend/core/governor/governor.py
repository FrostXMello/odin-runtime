"""Execution governor — final gate before any execution."""

from typing import Any

from odin_backend.core.context_graph.graph import GlobalContextGraph
from odin_backend.core.governor.decisions import (
    ExecutionRequest,
    GovernorDecision,
    GovernorDecisionType,
)
from odin_backend.core.kernel.state import CognitiveState
from odin_backend.core.bus.unified_bus import SignalUnificationBus
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger
from odin_backend.policies.engine import PolicyEngine
from odin_backend.security.trust import RuntimeTrustSystem

logger = get_logger(__name__)

HIGH_RISK_TOOLS = frozenset({"execute_terminal", "send_email", "write_file"})


class ExecutionGovernor:
    """Nothing executes without governor evaluation."""

    def __init__(
        self,
        event_bus: EventBus,
        policy_engine: PolicyEngine,
        trust_system: RuntimeTrustSystem,
        context_graph: GlobalContextGraph,
    ) -> None:
        self._event_bus = event_bus
        self._policy = policy_engine
        self._trust = trust_system
        self._graph = context_graph
        self._kernel: Any = None
        self._autonomy: Any = None
        self._coherence: Any = None
        self._recent_decisions: list[GovernorDecision] = []

    def set_kernel(self, kernel: Any) -> None:
        self._kernel = kernel

    def set_autonomy(self, autonomy: Any) -> None:
        self._autonomy = autonomy

    def set_coherence(self, coherence: Any) -> None:
        self._coherence = coherence

    async def evaluate(
        self,
        request: ExecutionRequest,
        *,
        cognitive_state: CognitiveState | None = None,
    ) -> GovernorDecision:
        state = cognitive_state or (self._kernel.get_state() if self._kernel else None)
        explain: dict[str, Any] = {
            "tool": request.tool_name,
            "agent": request.agent_id,
            "workflow_id": request.workflow_id,
            "graph_nodes": self._graph.snapshot().get("node_count", 0),
        }

        if self._coherence:
            report = self._coherence.last_report
            if report.conflict_report:
                decision = GovernorDecision(
                    decision=GovernorDecisionType.ESCALATE_TO_USER,
                    reason="Coherence conflicts detected — execution blocked until resolved",
                    explainable={**explain, "coherence": report.model_dump()},
                    remediation="; ".join(report.resolution_suggestions[:2]) or "Resolve conflicts",
                )
                await self._emit(decision, request)
                return decision
            if self._coherence.blocks_execution():
                decision = GovernorDecision(
                    decision=GovernorDecisionType.DEFER,
                    reason=f"Coherence score {report.coherence_score} below threshold — resolve conflicts first",
                    explainable={**explain, "coherence": report.model_dump()},
                    remediation="; ".join(report.resolution_suggestions[:2]) or "Run stability loop",
                )
                await self._emit(decision, request)
                return decision

        if self._autonomy:
            allowed, reason, auto_explain = self._autonomy.allows_execution(request)
            explain["autonomy"] = auto_explain
            if not allowed:
                decision = GovernorDecision(
                    decision=GovernorDecisionType.DENY,
                    reason=reason,
                    explainable=explain,
                    remediation="Elevate autonomy level or obtain user confirmation",
                )
                await self._emit(decision, request)
                return decision

        if request.tool_name in HIGH_RISK_TOOLS and not request.user_confirmed:
            decision = GovernorDecision(
                decision=GovernorDecisionType.ESCALATE_TO_USER,
                reason=f"High-risk tool '{request.tool_name}' requires explicit user confirmation",
                explainable=explain,
                remediation="Confirm in permissions panel or set user_confirmed=True",
            )
            await self._emit(decision, request)
            return decision

        try:
            agent_id = AgentId(request.agent_id)
        except ValueError:
            agent_id = AgentId.ODIN

        policy = await self._policy.evaluate(
            request.tool_name,
            params=request.params,
            workflow_id=request.workflow_id,
            agent_id=agent_id,
        )
        explain["policy"] = policy.model_dump()

        if not policy.allowed:
            decision = GovernorDecision(
                decision=GovernorDecisionType.DENY,
                reason=policy.reason,
                explainable=explain,
                remediation=policy.remediation,
            )
            await self._emit(decision, request)
            return decision

        trust = await self._trust.assess_execution(
            request.tool_name,
            params=request.params,
            workflow_id=request.workflow_id,
        )
        explain["trust_score"] = trust.trust_score
        explain["risk_level"] = trust.risk_level

        if trust.requires_escalation and not request.user_confirmed:
            decision = GovernorDecision(
                decision=GovernorDecisionType.REQUIRE_CLARIFICATION,
                reason=trust.explanation,
                explainable=explain,
                remediation="Provide clarification or user confirmation",
            )
            await self._emit(decision, request)
            return decision

        if state and state.system_health.get("degraded"):
            if request.tool_name in HIGH_RISK_TOOLS:
                decision = GovernorDecision(
                    decision=GovernorDecisionType.DEFER,
                    reason="System in degraded mode — deferring high-risk execution",
                    explainable=explain,
                )
                await self._emit(decision, request)
                return decision

        decision = GovernorDecision(
            decision=GovernorDecisionType.APPROVE,
            reason="Governor approved — proceed to Heimdall and execution",
            explainable=explain,
        )
        await self._emit(decision, request)
        return decision

    async def _emit(self, decision: GovernorDecision, request: ExecutionRequest) -> None:
        self._recent_decisions.append(decision)
        self._recent_decisions = self._recent_decisions[-50:]
        event = Event(
            type=EventType.GOVERNOR_DECISION,
            source=AgentId.ODIN,
            workflow_id=request.workflow_id,
            task_id=request.task_id,
            payload={
                "decision": decision.model_dump(),
                "request": request.model_dump(),
            },
        )
        if isinstance(self._event_bus, SignalUnificationBus):
            await self._event_bus.inner.publish(event)
        else:
            await self._event_bus.publish(event)

    def recent_decisions(self, limit: int = 20) -> list[dict[str, Any]]:
        return [d.model_dump() for d in self._recent_decisions[-limit:]]

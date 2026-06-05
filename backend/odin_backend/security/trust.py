"""Runtime trust system — scores, escalation, explainable blocks."""

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.policies.engine import PolicyEngine
from odin_backend.policies.models import PolicyDecision

TOOL_RISK: dict[str, float] = {
    "read_file": 0.1,
    "list_directory": 0.1,
    "search_web": 0.2,
    "summarize_content": 0.2,
    "get_browser_tabs": 0.2,
    "write_file": 0.6,
    "execute_terminal": 0.9,
    "send_email": 0.85,
    "open_browser": 0.4,
}


class TrustAssessment(BaseModel):
    tool_name: str
    trust_score: float
    risk_level: str
    requires_escalation: bool
    explanation: str
    policy_decision: dict[str, Any] | None = None


class RuntimeTrustSystem:
    def __init__(self, event_bus: EventBus, policy_engine: PolicyEngine) -> None:
        self._event_bus = event_bus
        self._policy = policy_engine
        self._workflow_sensitivity: dict[str, float] = {}
        self._anomalies: list[dict[str, Any]] = []

    def set_workflow_sensitivity(self, workflow_id: str, level: float) -> None:
        self._workflow_sensitivity[workflow_id] = min(1.0, max(0.0, level))

    async def assess_execution(
        self,
        tool_name: str,
        *,
        params: dict[str, Any] | None = None,
        workflow_id: str | None = None,
        workspace_trust: float = 0.8,
    ) -> TrustAssessment:
        base_risk = TOOL_RISK.get(tool_name, 0.5)
        wf_boost = self._workflow_sensitivity.get(workflow_id or "", 0.0)
        combined_risk = min(1.0, base_risk + wf_boost * 0.2)
        trust_score = round((1.0 - combined_risk) * workspace_trust, 3)

        policy_decision = await self._policy.evaluate(
            tool_name, params=params or {}, workflow_id=workflow_id
        )

        requires_escalation = combined_risk >= 0.7 or not policy_decision.allowed
        risk_level = "high" if combined_risk >= 0.7 else "medium" if combined_risk >= 0.4 else "low"

        explanation = (
            f"Trust score {trust_score:.2f} for '{tool_name}' (risk={risk_level}). "
            f"{policy_decision.reason or 'Policy checks applied.'}"
        )

        if requires_escalation and not policy_decision.allowed:
            await self._emit_escalation(tool_name, policy_decision)

        return TrustAssessment(
            tool_name=tool_name,
            trust_score=trust_score,
            risk_level=risk_level,
            requires_escalation=requires_escalation,
            explanation=explanation,
            policy_decision=policy_decision.model_dump(),
        )

    def record_anomaly(self, detail: str, metadata: dict | None = None) -> None:
        self._anomalies.append({"detail": detail, "metadata": metadata or {}})
        if len(self._anomalies) > 100:
            self._anomalies = self._anomalies[-100:]

    def explain_block(self, assessment: TrustAssessment) -> dict[str, Any]:
        pd = assessment.policy_decision or {}
        return {
            "blocked": not pd.get("allowed", True),
            "tool": assessment.tool_name,
            "trust_score": assessment.trust_score,
            "risk_level": assessment.risk_level,
            "explanation": assessment.explanation,
            "remediation": pd.get("remediation") or "Request approval via Heimdall panel",
            "policy": self._policy.explain_block(
                PolicyDecision.model_validate(pd) if pd else PolicyDecision(allowed=True)
            ),
        }

    def dashboard(self) -> dict[str, Any]:
        return {
            "recent_anomalies": self._anomalies[-10:],
            "tool_risk_map": TOOL_RISK,
            "sensitive_workflows": len(self._workflow_sensitivity),
        }

    async def _emit_escalation(self, tool_name: str, decision: PolicyDecision) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.SECURITY_ESCALATION,
                source=AgentId.HEIMDALL,
                payload={
                    "tool": tool_name,
                    "decision": decision.model_dump(),
                },
            )
        )

"""Mission governance — risk profile, coherence, governor path."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.models.mission import Mission
from odin_backend.models.task_graph import TaskNode


class MissionRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MissionRiskProfile(BaseModel):
    level: MissionRiskLevel = MissionRiskLevel.LOW
    requires_confirmation: bool = False
    requires_human_checkpoint: bool = False
    blocked_tools: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


HIGH_RISK_TOOLS = frozenset(
    {
        "execute_terminal",
        "write_file",
        "delete_file",
        "open_browser",
        "desktop_control",
    }
)


class MissionGovernance:
    """Pre-execution mission risk assessment."""

    def assess(self, mission: Mission, task: TaskNode | None = None) -> MissionRiskProfile:
        reasons: list[str] = []
        level = MissionRiskLevel.LOW
        tool = (task.output.get("tool") if task else None) or ""

        if mission.autonomy_level >= 4:
            level = MissionRiskLevel.MEDIUM
            reasons.append("high_autonomy_level")

        if tool in HIGH_RISK_TOOLS:
            level = MissionRiskLevel.HIGH
            reasons.append(f"high_risk_tool:{tool}")

        objective_lower = mission.objective.lower()
        if any(k in objective_lower for k in ("delete", "shutdown", "wire", "transfer funds")):
            level = MissionRiskLevel.CRITICAL
            reasons.append("critical_objective_keywords")

        requires_confirmation = level in (MissionRiskLevel.HIGH, MissionRiskLevel.CRITICAL)
        requires_checkpoint = level == MissionRiskLevel.CRITICAL

        return MissionRiskProfile(
            level=level,
            requires_confirmation=requires_confirmation,
            requires_human_checkpoint=requires_checkpoint,
            blocked_tools=list(HIGH_RISK_TOOLS) if level == MissionRiskLevel.CRITICAL else [],
            reasons=reasons,
        )

    async def validate_execution(
        self,
        app: Any,
        mission: Mission,
        task: TaskNode,
    ) -> tuple[bool, MissionRiskProfile, str]:
        """Coherence → risk → governor gate for mission task execution."""
        profile = self.assess(mission, task)
        if profile.requires_confirmation and not mission.human_approved:
            return False, profile, "human_approval_required"

        state = app.kernel.get_state()
        report = app.coherence.validate(state, app.kernel.recent_signals(20))
        if report.conflict_report and app.coherence.blocks_execution():
            return False, profile, "coherence_blocked"

        tool = task.output.get("tool", "noop")
        if tool == "noop":
            return True, profile, "noop_step"

        from odin_backend.core.governor.decisions import ExecutionRequest, GovernorDecisionType

        request = ExecutionRequest(
            tool_name=tool,
            agent_id=task.assigned_agent or "odin",
            params=task.output.get("params", {}),
            workflow_id=mission.mission_id,
            task_id=task.id,
            user_confirmed=mission.human_approved,
        )
        if hasattr(app, "execution_gate"):
            from odin_backend.core.execution_gate.gate import GateDecision

            gate = app.execution_gate.validate(app, request)
            if gate.decision == GateDecision.BLOCK:
                return False, profile, f"execution_gate:{gate.reason}"

        decision = await app.governor.evaluate(request, cognitive_state=state)
        if decision.decision != GovernorDecisionType.APPROVE:
            return False, profile, f"governor:{decision.decision.value}"

        if app.autonomy.current_level < mission.autonomy_level:
            return False, profile, "autonomy_level_insufficient"

        return True, profile, "approved"

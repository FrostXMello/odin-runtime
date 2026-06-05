"""
Governor decision DTOs — live in shared layer so tools/runtime never imports core.app.

Previously under core.governor.decisions; importing via core package root
pulled OdinApplication during agent module load.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class GovernorDecisionType(StrEnum):
    APPROVE = "approve"
    DENY = "deny"
    REQUIRE_CLARIFICATION = "require_clarification"
    DEFER = "defer"
    ESCALATE_TO_USER = "escalate_to_user"


class ExecutionRequest(BaseModel):
    tool_name: str
    agent_id: str
    params: dict[str, Any] = Field(default_factory=dict)
    workflow_id: str | None = None
    task_id: str | None = None
    user_confirmed: bool = False
    risk_level: float = 0.5


class GovernorDecision(BaseModel):
    decision: GovernorDecisionType
    reason: str
    explainable: dict[str, Any] = Field(default_factory=dict)
    remediation: str | None = None

    @property
    def allowed(self) -> bool:
        return self.decision == GovernorDecisionType.APPROVE

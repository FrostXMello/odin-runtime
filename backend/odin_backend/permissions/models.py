"""Permission classification models."""

from enum import StrEnum

from pydantic import BaseModel, Field

from odin_backend.models.task import AgentId


class PermissionClass(StrEnum):
    """Tool and action permission tiers."""

    SAFE = "safe"
    CONFIRM_REQUIRED = "confirm_required"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


class PermissionDecision(BaseModel):
    """Result of a permission check."""

    allowed: bool
    permission_class: PermissionClass
    tool_name: str
    agent_id: AgentId | None = None
    reason: str = ""
    requires_confirmation: bool = False
    metadata: dict = Field(default_factory=dict)

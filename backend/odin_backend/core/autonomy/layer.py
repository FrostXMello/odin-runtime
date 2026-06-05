"""Controlled autonomy — always context-scoped and governor-gated."""

from datetime import datetime, timezone
from enum import IntEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.governor.decisions import ExecutionRequest


class AutonomyLevel(IntEnum):
    NONE = 0  # read-only
    SUGGESTIONS = 1  # suggestions only
    PRE_APPROVED = 2  # pre-approved workflows
    BOUNDED = 3  # bounded execution with governor
    SUPERVISED = 4  # rare supervised autonomy


class AutonomyGrant(BaseModel):
    level: AutonomyLevel
    task_id: str | None = None
    workflow_id: str | None = None
    tools_allowed: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None
    granted_by: str = "user"


class AutonomyLayer:
    """Determines allowed execution scope before governor final decision."""

    def __init__(self, default_level: AutonomyLevel = AutonomyLevel.SUGGESTIONS) -> None:
        self._default_level = default_level
        self._grants: list[AutonomyGrant] = []
        self.current_level = int(default_level)

    def set_level(self, level: int) -> None:
        self.current_level = max(0, min(4, level))

    def grant(
        self,
        level: AutonomyLevel,
        *,
        workflow_id: str | None = None,
        tools: list[str] | None = None,
        duration_minutes: int = 30,
    ) -> AutonomyGrant:
        from datetime import timedelta

        grant = AutonomyGrant(
            level=level,
            workflow_id=workflow_id,
            tools_allowed=tools or [],
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=duration_minutes),
            granted_by="user",
        )
        self._grants.append(grant)
        return grant

    def _active_grants(self) -> list[AutonomyGrant]:
        now = datetime.now(timezone.utc)
        return [g for g in self._grants if g.expires_at is None or g.expires_at > now]

    def allows_execution(self, request: ExecutionRequest) -> tuple[bool, str, dict[str, Any]]:
        level = AutonomyLevel(self.current_level)
        explain: dict[str, Any] = {
            "autonomy_level": level.value,
            "active_grants": len(self._active_grants()),
        }

        if level == AutonomyLevel.NONE:
            return False, "Autonomy level 0 — read-only mode", explain

        if level == AutonomyLevel.SUGGESTIONS:
            return False, "Autonomy level 1 — suggestions only, execution requires elevation", explain

        for grant in self._active_grants():
            if grant.workflow_id and grant.workflow_id != request.workflow_id:
                continue
            if grant.tools_allowed and request.tool_name not in grant.tools_allowed:
                continue
            if grant.level >= AutonomyLevel.BOUNDED:
                explain["grant"] = grant.model_dump(mode="json")
                return True, f"Allowed by grant level {grant.level.value}", explain

        if level == AutonomyLevel.PRE_APPROVED:
            if request.workflow_id:
                return True, "Pre-approved workflow context", explain
            return False, "Pre-approved mode requires workflow_id", explain

        if level == AutonomyLevel.BOUNDED:
            safe_tools = {"read_file", "list_directory", "search_web", "summarize_content", "get_system_info"}
            if request.tool_name in safe_tools:
                return True, "Bounded autonomy — safe tool allowed", explain
            if request.user_confirmed:
                return True, "Bounded autonomy — user confirmed", explain
            # Scope allows evaluation; governor escalates/denies high-risk tools.
            return True, "Bounded autonomy — governor evaluates high-risk tool", explain

        if level == AutonomyLevel.SUPERVISED:
            if request.user_confirmed:
                return True, "Supervised autonomy with explicit user permission", explain
            return False, "Level 4 requires explicit user_confirmed", explain

        return False, "Autonomy scope denied", explain

"""Dynamic cognitive task groups."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

_TEAM_TEMPLATES = {
    "research_squad": ["research_analyst", "memory_curator"],
    "infrastructure_council": ["infrastructure_optimizer", "failure_diagnostician"],
    "planning_committee": ["planning_specialist", "execution_strategist"],
}


class CognitiveTeams:
    def __init__(self) -> None:
        self._teams: dict[str, dict[str, Any]] = {}

    def form(self, *, template: str, agent_ids: list[str]) -> dict[str, Any]:
        tid = str(uuid4())
        roles = _TEAM_TEMPLATES.get(template, ["generalist"])
        self._teams[tid] = {
            "id": tid,
            "template": template,
            "members": agent_ids,
            "roles": roles,
            "group_confidence": 0.5,
            "formed_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._teams[tid]

    def list_active(self) -> list[dict[str, Any]]:
        return list(self._teams.values())[-20:]

"""Plan recovery for failed missions."""

from __future__ import annotations

from typing import Any


def plan_recovery(*, mission_state: str, failed_tasks: int, blocked_tasks: int) -> dict[str, Any]:
    if failed_tasks > 0 and blocked_tasks == 0:
        return {"strategy": "retry_failed", "priority": "high"}
    if blocked_tasks > 0:
        return {"strategy": "heal_dependencies", "priority": "medium"}
    if mission_state == "blocked":
        return {"strategy": "resume_mission", "priority": "high"}
    return {"strategy": "observe", "priority": "low"}

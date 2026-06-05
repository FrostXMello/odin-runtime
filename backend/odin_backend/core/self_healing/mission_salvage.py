"""Salvage partially failed missions."""

from __future__ import annotations

from typing import Any


async def salvage_mission(app: Any, mission_id: str) -> dict[str, Any]:
    manager = getattr(app, "mission_manager", None)
    if not manager:
        return {"salvaged": False, "reason": "no_mission_manager"}
    mission = await manager.get(mission_id)
    if not mission:
        return {"salvaged": False, "reason": "mission_not_found"}
    completed = len(mission.completed_tasks or [])
    failed = len(mission.failed_tasks or [])
    return {
        "salvaged": completed > 0,
        "mission_id": mission_id,
        "completed": completed,
        "failed": failed,
        "partial": completed > 0 and failed > 0,
    }

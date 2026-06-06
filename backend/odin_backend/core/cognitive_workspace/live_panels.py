from __future__ import annotations
from typing import Any


def panel_snapshot(*, app: Any) -> dict[str, Any]:
    agents = []
    if hasattr(app, "agent_society"):
        agents = list(getattr(app.agent_society, "_agents", {}).keys())[:12]
    missions = []
    if hasattr(app, "mission_manager"):
        missions = [getattr(m, "mission_id", str(i)) for i, m in enumerate(getattr(app.mission_manager, "_missions", {}).values())][:8]
    return {"agents": agents, "missions": missions, "live": True}

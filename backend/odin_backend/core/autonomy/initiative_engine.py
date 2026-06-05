"""Proactive initiative generation from objectives and environment."""

from __future__ import annotations

from typing import Any

from odin_backend.core.autonomy.objective_graph import PersistentObjective


class InitiativeEngine:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def propose_initiatives(self, *, alerts: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        initiatives: list[dict[str, Any]] = []
        objectives = await self._app.objective_manager.graph.top_priority(limit=3)
        for obj in objectives:
            initiatives.append(
                {
                    "kind": "objective",
                    "objective_id": obj.objective_id,
                    "title": obj.title,
                    "priority": obj.priority,
                    "mission_objective": await self._app.objective_manager.mission_objective_for(obj),
                }
            )
        for alert in alerts or []:
            if alert.get("severity", "low") in ("high", "critical"):
                initiatives.append(
                    {
                        "kind": "environment_response",
                        "alert": alert,
                        "mission_objective": f"[Autonomous] Respond to {alert.get('kind')}: {alert.get('message', '')}"[:500],
                        "priority": 0.8,
                    }
                )
        initiatives.sort(key=lambda x: -x.get("priority", 0.5))
        return initiatives[:5]

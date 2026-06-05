"""Operational planning orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.operational_planning.long_horizon_scheduler import LongHorizonScheduler
from odin_backend.core.operational_planning.milestone_projection import project_milestones
from odin_backend.core.operational_planning.objective_forecasting import forecast
from odin_backend.core.operational_planning.strategic_roadmaps import build_roadmap
from odin_backend.core.operational_planning.sustainability_engine import assess


class OperationalPlanningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._scheduler = LongHorizonScheduler()

    async def project(self, *, goal: str, horizon_weeks: int = 4) -> dict[str, Any]:
        if not getattr(self._app.settings, "operational_planning_enabled", False):
            return {"accepted": False, "reason": "operational_planning_disabled"}
        roadmap = build_roadmap(goal=goal, milestones=horizon_weeks)
        milestones = project_milestones(roadmap)
        fc = forecast(objectives=len(roadmap), horizon_weeks=horizon_weeks)
        sustainability = assess(load=0.3, budget_remaining=5000.0)
        scheduled = self._scheduler.schedule(title=goal, horizon_days=horizon_weeks * 7)
        return {
            "accepted": True,
            "roadmap": roadmap,
            "milestones": milestones,
            "forecast": fc,
            "sustainability": sustainability,
            "scheduled": scheduled,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"scheduled_items": len(self._scheduler.list_all()), "items": self._scheduler.list_all()[-5:]}

from __future__ import annotations
from typing import Any


class UpgradePlanningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def plan(self, *, goal: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_evolution_enabled", False):
            return {"accepted": False, "reason": "engineering_evolution_disabled"}
        proposal = {"goal": goal[:80], "approval_required": True, "rollback_plan": "mandatory"}
        self._emit("engineering_upgrade_proposed", proposal)
        return {"accepted": True, "proposal": proposal, "auto_deploy": False}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="upgrade_planning")

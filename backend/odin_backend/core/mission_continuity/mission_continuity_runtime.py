"""Mission continuity runtime (Prompt 55)."""
from __future__ import annotations
from typing import Any


class MissionContinuityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._health = 0.75

    async def build_mission_resume_chain(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "mission_continuity_enabled", False):
            return {"accepted": False, "reason": "mission_continuity_disabled"}
        chain = []
        if hasattr(self._app, "workspace_sessions"):
            r = await self._app.workspace_sessions.build_resume_chain()
            chain.extend(r.get("chain", []))
        if hasattr(self._app, "continuity_forecasting"):
            cf = await self._app.continuity_forecasting.detect_abandoned_work()
            if cf.get("accepted"):
                chain.append("abandoned_work")
        self._emit("mission_resume_chain_built", {"steps": len(chain)})
        return {"accepted": True, "chain": chain, "supervised": True}

    async def detect_interrupted_workflows(self) -> dict[str, Any]:
        interrupted = []
        if hasattr(self._app, "deferred_reasoning"):
            snap = self._app.deferred_reasoning.snapshot()
            if snap.get("pending", 0) > 0:
                interrupted.append("deferred_reasoning")
        if interrupted:
            self._emit("workflow_interruption_detected", {"count": len(interrupted)})
        return {"accepted": True, "interrupted": interrupted, "operator_visible": True}

    async def restore_mission_context(self) -> dict[str, Any]:
        if hasattr(self._app, "workspace_sessions"):
            return await self._app.workspace_sessions.restore_workspace_session()
        return {"accepted": True, "restored": False}

    async def estimate_continuity_health(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "continuity_tracking_enabled", True):
            return {"accepted": True, "health": self._health, "tracking": False}
        if hasattr(self._app, "operator_focus"):
            snap = self._app.operator_focus.snapshot()
            if snap.get("active"):
                self._health = min(1.0, self._health + 0.05)
        return {"accepted": True, "health": round(self._health, 2), "bounded": True}

    def snapshot(self) -> dict[str, Any]:
        return {"health": self._health}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="mission_continuity")

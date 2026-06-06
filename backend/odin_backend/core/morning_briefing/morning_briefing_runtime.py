"""Morning briefing runtime (Prompt 53)."""
from __future__ import annotations
from typing import Any


class MorningBriefingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._last_summary: dict = {}

    async def build_morning_briefing(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "morning_briefing_enabled", False):
            return {"accepted": False, "reason": "morning_briefing_disabled"}
        overnight = await self.summarize_overnight_activity()
        focus = await self.generate_focus_plan()
        briefing = {
            "executive_summary": "Overnight cognition completed within bounded limits.",
            "overnight_findings": overnight.get("summary", {}),
            "focus_plan": focus.get("plan", {}),
            "supervised": True,
        }
        self._last_summary = briefing
        self._emit("morning_briefing_generated", {"sections": 3})
        return {"accepted": True, "briefing": briefing}

    async def summarize_overnight_activity(self) -> dict[str, Any]:
        summary = {"cycles": 0, "findings": []}
        if hasattr(self._app, "overnight_cognition"):
            summary["cycles"] = self._app.overnight_cognition.snapshot().get("cycles", 0)
        return {"accepted": True, "summary": summary}

    async def generate_focus_plan(self) -> dict[str, Any]:
        plan = {"priorities": ["review overnight findings", "resume deferred work"], "transparent": True}
        if hasattr(self._app, "continuity_forecasting"):
            cf = await self._app.continuity_forecasting.generate_continuity_plan()
            plan["continuity"] = cf
        return {"accepted": True, "plan": plan}

    def snapshot(self) -> dict[str, Any]:
        return {"has_briefing": bool(self._last_summary)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="morning_briefing")

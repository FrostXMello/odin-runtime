"""Daily driver desktop experience orchestrator."""
from __future__ import annotations
from typing import Any


class DailyOperatorExperienceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def startup(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "daily_operator_experience_enabled", False):
            return {"accepted": False, "reason": "daily_operator_experience_disabled"}
        briefing = {}
        if hasattr(self._app, "daily_workflow"):
            briefing = await self._app.daily_workflow.startup_routine()
        rehydrated = {}
        if hasattr(self._app, "persistent_cognition"):
            rehydrated = await self._app.persistent_cognition.rehydrate_session()
            self._emit("workspace_rehydrated", rehydrated)
        workspace = {}
        if hasattr(self._app, "workspace_presence"):
            workspace = await self._app.workspace_presence.restore_session()
        continuity = {}
        if hasattr(self._app, "daily_continuity"):
            continuity = await self._app.daily_continuity.resume_summary()
        return {
            "accepted": True,
            "briefing": briefing,
            "rehydrated": rehydrated,
            "workspace": workspace,
            "continuity": continuity,
            "morning_summary": continuity.get("narrative"),
        }

    async def focus_shift(self, *, focus: str) -> dict[str, Any]:
        self._emit("operator_focus_shifted", {"focus": focus[:80]})
        if hasattr(self._app, "live_environment"):
            await self._app.live_environment.update(duration_s=120, reason=focus)
        return {"accepted": True, "focus": focus}

    async def evolution_review(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "daily_operator_experience_enabled", False):
            return {"accepted": False, "reason": "daily_operator_experience_disabled"}
        review = {}
        if hasattr(self._app, "self_evolution"):
            review["evolution"] = self._app.self_evolution.snapshot()
        if hasattr(self._app, "runtime_benchmarks"):
            review["benchmarks"] = self._app.runtime_benchmarks.snapshot()
        if hasattr(self._app, "autonomous_patching"):
            review["patching"] = self._app.autonomous_patching.snapshot()
        self._emit("evolution_review_opened", {"sections": list(review.keys())})
        return {"accepted": True, "review": review, "approval_required": True}

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": getattr(self._app.settings, "daily_operator_experience_enabled", False)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="daily_operator_experience")

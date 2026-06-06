"""Daily and weekly continuity orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.daily_continuity.continuity_predictions import predict
from odin_backend.core.daily_continuity.continuity_timeline import Timeline
from odin_backend.core.daily_continuity.daily_memory import record
from odin_backend.core.daily_continuity.project_presence import presence
from odin_backend.core.daily_continuity.session_narratives import narrative
from odin_backend.core.daily_continuity.unfinished_work import UnfinishedWork
from odin_backend.core.daily_continuity.weekly_context import week_context


class DailyContinuityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._timeline = Timeline()
        self._unfinished = UnfinishedWork()
        self._last_action = ""

    async def record_day(self, *, summary: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "daily_continuity_enabled", False):
            return {"accepted": False, "reason": "daily_continuity_disabled"}
        mem = record(summary=summary)
        self._timeline.add(mem)
        return {"accepted": True, "memory": mem}

    async def track_unfinished(self, *, title: str, project: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "daily_continuity_enabled", False):
            return {"accepted": False, "reason": "daily_continuity_disabled"}
        item = self._unfinished.track(title=title, project=project)
        self._emit("unfinished_work_detected", item)
        return {"accepted": True, "item": item}

    async def resume_summary(self) -> dict[str, Any]:
        abandoned = self._unfinished.abandoned()
        pred = predict(last_action=self._last_action or "startup")
        self._emit("workflow_prediction_generated", pred)
        return {
            "accepted": True,
            "unfinished": abandoned,
            "prediction": pred,
            "timeline": self._timeline.snapshot(),
            "narrative": narrative(sessions=self._timeline.snapshot(5)),
            "weekly": week_context(items=[e.get("summary", "") for e in self._timeline.snapshot(7)]),
        }

    async def project(self, *, name: str, active: bool = True) -> dict[str, Any]:
        return {"accepted": True, "presence": presence(project=name, active=active)}

    def snapshot(self) -> dict[str, Any]:
        return {"timeline_len": len(self._timeline.snapshot(100)), "unfinished": len(self._unfinished.abandoned())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="daily_continuity")

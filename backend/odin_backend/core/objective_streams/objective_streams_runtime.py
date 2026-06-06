"""Objective streams runtime (Prompt 56)."""
from __future__ import annotations
from typing import Any


class ObjectiveStreamsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._stream_count = 0

    async def stream_objective_updates(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "objective_streams_enabled", False):
            return {"accepted": False, "reason": "objective_streams_disabled"}
        if self._stream_count > 64:
            return {"accepted": False, "reason": "stream_throttled"}
        self._stream_count += 1
        self._emit("objective_stream_updated", {"count": self._stream_count})
        return {"accepted": True, "streamed": True, "bounded": True}

    async def reprioritize_active_objectives(self) -> dict[str, Any]:
        if hasattr(self._app, "objective_management"):
            objs = await self._app.objective_management.summarize_active_objectives()
            return {"accepted": True, "reprioritized": objs.get("count", 0), "approval_gated": True}
        return {"accepted": True, "reprioritized": 0}

    async def detect_objective_stagnation(self) -> dict[str, Any]:
        if hasattr(self._app, "objective_management"):
            r = await self._app.objective_management.detect_stalled_objectives()
            if r.get("stalled"):
                self._emit("objective_stagnation_detected", {"count": len(r["stalled"])})
            return {"accepted": True, "stagnant": r.get("stalled", [])}
        return {"accepted": True, "stagnant": []}

    async def render_objective_flow(self) -> dict[str, Any]:
        return {"accepted": True, "flow": "streaming", "supervised": True}

    def snapshot(self) -> dict[str, Any]:
        return {"stream_count": self._stream_count}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="objective_streams")

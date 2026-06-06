"""Live overlays V2 (Prompt 54)."""
from __future__ import annotations
from typing import Any


class LiveOverlaysV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._attached: dict[str, bool] = {}
        self._suppressed: set[str] = set()
        self._mode = "adaptive"

    async def attach_overlay(self, *, overlay_type: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "live_overlays_v2_enabled", False):
            return {"accepted": False, "reason": "live_overlays_v2_disabled"}
        if overlay_type in self._suppressed:
            return {"accepted": False, "reason": "overlay_suppressed"}
        self._attached[overlay_type] = True
        self._emit("overlay_context_updated", {"overlay": overlay_type[:40]})
        return {"accepted": True, "overlay": overlay_type, "throttled": self._mode == "adaptive"}

    async def suppress_overlay(self, *, overlay_type: str) -> dict[str, Any]:
        self._suppressed.add(overlay_type[:40])
        self._attached.pop(overlay_type, None)
        self._emit("overlay_suppressed", {"overlay": overlay_type[:40]})
        return {"accepted": True, "suppressed": overlay_type}

    async def update_overlay_context(self, *, context: str) -> dict[str, Any]:
        self._emit("overlay_context_updated", {"context": context[:80]})
        return {"accepted": True, "context": context[:80]}

    async def render_focus_overlay(self) -> dict[str, Any]:
        if "focus_timer" in self._suppressed:
            return {"accepted": False, "reason": "suppressed"}
        return await self.attach_overlay(overlay_type="focus_timer")

    def snapshot(self) -> dict[str, Any]:
        return {"attached": list(self._attached.keys()), "suppressed": list(self._suppressed)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_overlays_v2")

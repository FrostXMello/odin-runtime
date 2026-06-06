"""Unified cognitive surface orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_surface.attention_surface import surface as attn_surface
from odin_backend.core.cognitive_surface.cognition_panels import panels
from odin_backend.core.cognitive_surface.mission_surface import mission
from odin_backend.core.cognitive_surface.overlay_compositor import compose
from odin_backend.core.cognitive_surface.reasoning_surface import reasoning


class CognitiveSurfaceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def render(self, *, mission_id: str = "", focus: str = "workspace", steps: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_surface_enabled", False):
            return {"accepted": False, "reason": "cognitive_surface_disabled"}
        layers = ["presence", "attention", "reasoning"]
        if mission_id:
            layers.append("mission")
        comp = compose(layers=layers)
        surf = {
            "panels": panels(count=4),
            "attention": attn_surface(focus=focus),
            "reasoning": reasoning(steps=steps or ["observe", "plan"]),
            "mission": mission(mission_id=mission_id, state="active") if mission_id else None,
            "compositor": comp,
        }
        self._emit("cognitive_surface_updated", {"layers": len(layers)})
        return {"accepted": True, "surface": surf, "gpu_safe": True}

    def snapshot(self) -> dict[str, Any]:
        return {"unified": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_surface")

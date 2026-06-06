"""Immersive cognitive UI orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.immersive_ui.adaptive_panels import panels
from odin_backend.core.immersive_ui.ambient_presence import ambient
from odin_backend.core.immersive_ui.cinematic_mode import cinematic
from odin_backend.core.immersive_ui.cognitive_animation import animation
from odin_backend.core.immersive_ui.dynamic_layouts import MODES, layout
from odin_backend.core.immersive_ui.focus_modes import focus


class ImmersiveUiRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        mode = getattr(app.settings, "native_desktop_mode", "balanced")
        self._mode = mode if mode in MODES else "balanced"

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "immersive_ui_enabled", False):
            return {"accepted": False, "reason": "immersive_ui_disabled"}
        self._mode = mode if mode in MODES else "balanced"
        lay = layout(self._mode)
        self._emit("immersive_mode_changed", {"mode": self._mode, "fps_cap": lay["fps_cap"]})
        return {"accepted": True, "layout": lay, "animation": animation(thinking=False), "focus": focus(distraction_free=self._mode == "minimal")}

    async def render(self, *, thinking: bool = False, idle: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "immersive_ui_enabled", False):
            return {"accepted": False, "reason": "immersive_ui_disabled"}
        lay = layout(self._mode)
        return {
            "accepted": True,
            "mode": self._mode,
            "layout": lay,
            "animation": animation(thinking=thinking),
            "panels": panels(count=lay["columns"]),
            "cinematic": cinematic(self._mode == "cinematic"),
            "ambient": ambient(idle=idle),
            "gpu_safe": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "modes": list(MODES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="immersive_ui")

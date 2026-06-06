"""Operator command surfaces runtime (Prompt 60)."""
from __future__ import annotations
from typing import Any


class OperatorCommandSurfacesRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._density = "balanced"
        self._render_count = 0

    async def render_command_surface(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_command_surfaces_enabled", False):
            return {"accepted": False, "reason": "operator_command_surfaces_disabled"}
        if self._render_count > 56:
            return {"accepted": False, "reason": "render_throttled"}
        self._render_count += 1
        self._emit("command_surface_rendered", {"density": self._density})
        return {"accepted": True, "rendered": True, "lazy_hydration": True}

    async def render_operational_overlay(self) -> dict[str, Any]:
        self._emit("operational_overlay_updated", {"overlay": True})
        return {"accepted": True, "overlay": True, "cinematic_safe": True}

    async def compress_visual_surfaces(self) -> dict[str, Any]:
        self._density = "compact"
        return {"accepted": True, "density": self._density, "low_power": True}

    async def prioritize_operator_visibility(self) -> dict[str, Any]:
        return {"accepted": True, "prioritized": True, "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"density": self._density, "render_count": self._render_count}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_command_surfaces")

"""Cognitive visual layers runtime (Prompt 56)."""
from __future__ import annotations
from typing import Any


class CognitiveVisualLayersRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._density = "balanced"
        self._render_mode = "adaptive"

    async def render_runtime_constellation(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_visual_layers_enabled", False):
            return {"accepted": False, "reason": "cognitive_visual_layers_disabled"}
        self._render_mode = getattr(self._app.settings, "cognitive_render_mode", "adaptive")
        self._emit("runtime_constellation_rendered", {"mode": self._render_mode})
        return {"accepted": True, "constellation": True, "lazy_hydration": True}

    async def render_objective_river(self) -> dict[str, Any]:
        self._emit("objective_river_rendered", {"density": self._density})
        return {"accepted": True, "river": True, "throttled": self._render_mode == "adaptive"}

    async def render_attention_heatmap(self) -> dict[str, Any]:
        if hasattr(self._app, "desktop_attention"):
            await self._app.desktop_attention.prioritize_desktop_attention()
        return {"accepted": True, "heatmap": True, "low_power": self._density == "compact"}

    async def compress_visual_density(self) -> dict[str, Any]:
        self._density = getattr(self._app.settings, "visual_density", "balanced")
        if self._density == "compact":
            self._density = "compact"
        self._emit("cognitive_visual_density_compressed", {"density": self._density})
        return {"accepted": True, "density": self._density, "cinematic_safe": True}

    def snapshot(self) -> dict[str, Any]:
        return {"density": self._density, "render_mode": self._render_mode}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_visual_layers")

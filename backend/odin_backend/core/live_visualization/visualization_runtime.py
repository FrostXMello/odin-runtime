"""Live cognitive visualization orchestrator."""
from __future__ import annotations
from typing import Any


class LiveVisualizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._fps_cap = 30

    async def render(self, *, view: str = "reasoning_dag") -> dict[str, Any]:
        if not getattr(self._app.settings, "live_visualization_enabled", False):
            return {"accepted": False, "reason": "live_visualization_disabled"}
        mode = getattr(self._app.settings, "native_desktop_mode", "balanced")
        self._fps_cap = {"compact": 15, "balanced": 30, "immersive": 45, "cinematic": 60}.get(mode, 30)
        graph = {"nodes": [], "edges": []}
        if hasattr(self._app, "reasoning_streams"):
            r = await self._app.reasoning_streams.push(thought=f"viz:{view}")
            graph = r.get("decisions", graph)
        society = {"agents": []}
        if hasattr(self._app, "agent_society"):
            society = {"agents": list(getattr(self._app.agent_society, "_agents", {}).keys())[:8]}
        self._emit("visualization_synced", {"view": view, "fps_cap": self._fps_cap})
        self._emit("live_reasoning_rendered", {"view": view})
        return {
            "accepted": True,
            "view": view,
            "graph": graph,
            "society": society,
            "fps_cap": self._fps_cap,
            "lazy_render": True,
            "gpu_safe": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"fps_cap": self._fps_cap}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_visualization")

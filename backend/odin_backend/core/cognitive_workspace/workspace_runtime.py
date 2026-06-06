"""Unified cognitive workspace orchestrator (Prompt 46)."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

from odin_backend.core.cognitive_workspace.attention_router import route_attention
from odin_backend.core.cognitive_workspace.cognitive_focus import focus_profile
from odin_backend.core.cognitive_workspace.layout_engine import build_layout
from odin_backend.core.cognitive_workspace.live_panels import panel_snapshot
from odin_backend.core.cognitive_workspace.session_layouts import SessionLayouts

WORKSPACE_MODES = ("minimal", "operator", "engineering", "immersive", "cinematic")
RESOURCE_PROFILES = ("ultra_light", "balanced", "immersive", "cinematic")


class CognitiveWorkspaceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._id = str(uuid4())
        self._mode = "operator"
        self._profile = "balanced"
        self._layouts = SessionLayouts()
        self._panels = build_layout(mode=self._mode)["panels"]

    async def open(self, *, mode: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_workspace_enabled", False):
            return {"accepted": False, "reason": "cognitive_workspace_disabled"}
        if mode in WORKSPACE_MODES:
            self._mode = mode
        layout = build_layout(mode=self._mode, panels=self._panels)
        restored = self._layouts.restore()
        if restored.get("restored"):
            layout = restored.get("layout", layout)
        live = panel_snapshot(app=self._app)
        focus = focus_profile(self._mode)
        self._emit("workspace_focus_changed", {"mode": self._mode, "workspace_id": self._id})
        self._emit("cognitive_transition_rendered", {"transition": "workspace_open"})
        return {
            "accepted": True,
            "workspace_id": self._id,
            "mode": self._mode,
            "modes": list(WORKSPACE_MODES),
            "layout": layout,
            "live": live,
            "focus": focus,
            "resource_profile": self._profile,
            "supervised": True,
        }

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if mode not in WORKSPACE_MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        layout = build_layout(mode=mode)
        self._layouts.persist(layout)
        routed = route_attention(focus=mode, panels=layout["panels"])
        self._emit("workspace_focus_changed", routed)
        return {"accepted": True, "mode": mode, "layout": layout, "routing": routed}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in RESOURCE_PROFILES:
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        caps = {"ultra_light": 15, "balanced": 30, "immersive": 45, "cinematic": 60}
        return {
            "accepted": True,
            "profile": profile,
            "fps_cap": caps.get(profile, 30),
            "stream_throttle": profile == "ultra_light",
            "lazy_render": True,
        }

    async def quick_command(self, *, query: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_workspace_enabled", False):
            return {"accepted": False, "reason": "cognitive_workspace_disabled"}
        resp = {}
        if hasattr(self._app, "conversational_os"):
            resp = await self._app.conversational_os.interact(text=query)
        return {"accepted": True, "query": query, "response": resp}

    def snapshot(self) -> dict[str, Any]:
        return {
            "workspace_id": self._id,
            "mode": self._mode,
            "profile": self._profile,
            "panels": self._panels,
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_workspace")

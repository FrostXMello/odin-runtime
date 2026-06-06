"""Unified cognitive shell orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognitive_shell.adaptive_ui_state import ui_state
from odin_backend.core.cognitive_shell.attention_visualizer import visualize_attention
from odin_backend.core.cognitive_shell.cognitive_presence import compute_presence
from odin_backend.core.cognitive_shell.conversational_context import build_context
from odin_backend.core.cognitive_shell.interaction_state import InteractionState
from odin_backend.core.cognitive_shell.live_state_router import route_state
from odin_backend.core.cognitive_shell.session_orchestrator import merge_session, start_session
from odin_backend.core.cognitive_shell.workspace_presence import workspace_presence


class CognitiveShellRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._session = start_session()
        self._interaction = InteractionState()
        self._presence = compute_presence(active=True, focus="shell", energy=0.5)
        self._ui = ui_state(mode=getattr(app.settings, "cognitive_interface_mode", "balanced"))

    async def activate(self, *, workspace: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_shell_enabled", False):
            return {"accepted": False, "reason": "cognitive_shell_disabled"}
        ws = workspace or {}
        self._presence = compute_presence(
            active=True,
            focus=ws.get("active_app", "workspace"),
            energy=ws.get("energy", 0.55),
        )
        ctx = build_context(workspace=ws)
        wp = workspace_presence(app=ws.get("active_app", "unknown"), title=ws.get("title", ""))
        self._session = merge_session(self._session, {"turn_delta": 0, "workspace": wp})
        self._emit("presence_shifted", {"state": self._presence["state"], "simulated": True})
        self._emit("workspace_attention_changed", {"app": wp["app"], "label": wp["context_label"]})
        return {"accepted": True, "presence": self._presence, "context": ctx, "workspace": wp}

    async def route_live(self, *, channel: str, payload: dict) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_shell_enabled", False):
            return {"accepted": False, "reason": "cognitive_shell_disabled"}
        routed = route_state(channel=channel, payload=payload)
        if routed["accepted"]:
            self._emit("reasoning_stream_updated", {"channel": channel})
        return routed

    async def set_ui_mode(self, mode: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_shell_enabled", False):
            return {"accepted": False, "reason": "cognitive_shell_disabled"}
        self._ui = ui_state(mode=mode)
        return {"accepted": True, "ui": self._ui}

    def snapshot(self) -> dict[str, Any]:
        nodes = [{"id": "shell", "weight": 1.0}, {"id": "workspace", "weight": 0.8}]
        return {
            "session": self._session,
            "presence": self._presence,
            "interaction": self._interaction.snapshot(),
            "attention": visualize_attention(nodes=nodes),
            "ui": self._ui,
            "disclosure": "simulated_presence",
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_shell")

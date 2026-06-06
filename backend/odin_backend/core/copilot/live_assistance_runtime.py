"""Live copilot orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.copilot.live_assistance.collaborative_editing_context import editing_context
from odin_backend.core.copilot.live_assistance.contextual_suggestions import suggest
from odin_backend.core.copilot.live_assistance.conversation_context_engine import ConversationContext
from odin_backend.core.copilot.live_assistance.engineering_overlay import overlay_hints
from odin_backend.core.copilot.live_assistance.realtime_debug_assist import debug_assist


class LiveCopilotRuntime:
    MODES = ("passive", "suggestive", "collaborative", "supervised-action")

    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "suggestive"
        self._conversation = ConversationContext()

    async def assist(self, *, context: dict, mode: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "live_copilot_enabled", False):
            return {"accepted": False, "reason": "live_copilot_disabled"}
        active_mode = mode or self._mode
        if active_mode not in self.MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        if active_mode == "supervised-action":
            active_mode = "supervised-action"
        suggestions = suggest(context=context)
        debug = debug_assist(context) if context.get("error") else None
        hints = overlay_hints(context=context)
        conv = self._conversation.update(context)
        edit_ctx = editing_context(open_files=context.get("open_files", []))
        self._emit("realtime_assistance_generated", {"mode": active_mode, "suggestions": len(suggestions)})
        return {
            "accepted": True,
            "mode": active_mode,
            "suggestions": suggestions,
            "debug": debug,
            "overlay": hints,
            "conversation": conv,
            "editing": edit_ctx,
            "supervised": active_mode == "supervised-action",
        }

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if mode not in self.MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        return {"accepted": True, "mode": mode}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "conversation_turns": self._conversation.turns()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_copilot")

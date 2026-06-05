"""Production copilot runtime extending existing copilot."""

from __future__ import annotations

from typing import Any

from odin_backend.core.copilot.attention_model import AttentionModel
from odin_backend.core.copilot.contextual_help import generate_help
from odin_backend.core.copilot.operator_intent import detect_intent
from odin_backend.core.copilot.proactive_workspace_assistance import suggest
from odin_backend.core.copilot.realtime_assistant import assist
from odin_backend.core.copilot.ui_understanding import understand


class CopilotProductionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._attention = AttentionModel()
        self._actions: list[str] = []

    async def process_snapshot(self, snapshot: dict) -> dict[str, Any]:
        if not getattr(self._app.settings, "copilot_production_enabled", False):
            return {"accepted": False, "reason": "copilot_production_disabled"}
        ui = understand(snapshot)
        self._attention.update(app=ui["app"], duration_s=snapshot.get("focus_duration_s", 0))
        assistance = await assist(self._app, context=snapshot)
        intent = detect_intent(self._actions[-10:])
        proactive = suggest(focus_app=ui["app"], patterns=self._actions)
        help_ctx = generate_help(app=ui["app"], task=intent.get("intent", "work"))
        return {
            "accepted": True,
            "ui": ui,
            "assistance": assistance,
            "intent": intent,
            "proactive": proactive,
            "help": help_ctx,
            "attention": self._attention.update(app=ui["app"], duration_s=snapshot.get("focus_duration_s", 0)),
        }

    def record_action(self, action: str) -> None:
        self._actions.append(action)

    def snapshot(self) -> dict[str, Any]:
        base = {}
        if hasattr(self._app, "copilot_runtime"):
            base = self._app.copilot_runtime.snapshot()
        return {**base, "attention_app": self._attention._focus_app, "action_count": len(self._actions)}

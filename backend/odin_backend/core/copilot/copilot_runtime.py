"""Live copilot runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.copilot.assistance_modes import CopilotMode
from odin_backend.core.copilot.context_actions import contextual_actions
from odin_backend.core.copilot.suggestion_engine import generate_suggestions
from odin_backend.core.copilot.workflow_prediction import predict_next


class CopilotRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        mode = getattr(app.settings, "copilot_mode", CopilotMode.PASSIVE_OBSERVER.value)
        try:
            self._mode = CopilotMode(mode)
        except ValueError:
            self._mode = CopilotMode.PASSIVE_OBSERVER
        self._suggestions: list[dict] = []

    @property
    def mode(self) -> CopilotMode:
        return self._mode

    def set_mode(self, mode: str) -> None:
        try:
            self._mode = CopilotMode(mode)
        except ValueError:
            pass

    async def tick(self) -> dict[str, Any]:
        if self._mode == CopilotMode.PASSIVE_OBSERVER:
            return {"mode": self._mode.value, "suggestions": []}
        ctx: dict[str, Any] = {}
        if hasattr(self._app, "multimodal_perception"):
            ctx = self._app.multimodal_perception.snapshot()
        ctx["summary"] = ctx.get("context", {}).get("summary", "")
        self._suggestions = await generate_suggestions(self._app, context=ctx)
        for s in self._suggestions:
            self._emit("copilot_suggestion_generated", s)
        if self._mode in (CopilotMode.ACTIVE_COPILOT, CopilotMode.AUTONOMOUS_ASSISTANT):
            self._emit("proactive_assistance_triggered", {"count": len(self._suggestions)})
        return {"mode": self._mode.value, "suggestions": self._suggestions}

    async def recommend_actions(self, scene: dict[str, Any]) -> list[dict[str, str]]:
        return contextual_actions(scene)

    async def propose_suggestion(self, suggestion: dict[str, Any]) -> dict[str, Any] | None:
        if not getattr(self._app.settings, "action_engine_enabled", False):
            return None
        kind = suggestion.get("propose_kind", "copilot_suggestion")
        return await self._app.action_runtime.propose(
            kind=kind,
            label=str(suggestion.get("title", "Copilot action")),
            payload={"message": suggestion.get("message", "")},
        )

    def snapshot(self, *, patterns: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return {
            "mode": self._mode.value,
            "suggestions": self._suggestions[-10:],
            "predicted_next": predict_next(patterns or []),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="copilot_runtime")

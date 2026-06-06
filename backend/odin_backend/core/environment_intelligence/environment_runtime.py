"""Live environment intelligence (Prompt 48)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.environment_intelligence.attention_tracking import track
from odin_backend.core.environment_intelligence.context_classifier import classify
from odin_backend.core.environment_intelligence.environment_memory import EnvironmentMemory
from odin_backend.core.environment_intelligence.operator_patterns import patterns
from odin_backend.core.environment_intelligence.window_semantics import semantics
from odin_backend.core.environment_intelligence.workflow_prediction import predict
from odin_backend.core.environment_intelligence.workspace_understanding import understand


class EnvironmentIntelligenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._memory = EnvironmentMemory()

    async def observe(self, *, repo: str = "", file: str = "", title: str = "", app_name: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "environment_intelligence_enabled", False):
            return {"accepted": False, "reason": "environment_intelligence_disabled"}
        ws = understand(repo=repo or "local", file=file)
        win = semantics(title=title, app=app_name or "editor")
        attn = track(focus=file or repo)
        pred = predict(intent=ws.get("intent", "work"))
        kind = classify(context=file or repo)
        entry = {"ws": ws, "window": win, "prediction": pred}
        self._memory.remember(entry)
        self._emit("environment_context_detected", {"kind": kind, "repo": repo})
        self._emit("workflow_prediction_generated", pred)
        if hasattr(self._app, "live_environment"):
            await self._app.live_environment.update(duration_s=60, reason=kind)
        return {
            "accepted": True,
            "understanding": ws,
            "attention": attn,
            "patterns": patterns(switches=2),
            "prediction": pred,
            "memory": self._memory.recent(),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"entries": len(self._memory.recent())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="environment_intelligence")

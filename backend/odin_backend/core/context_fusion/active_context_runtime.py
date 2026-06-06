"""Active context fusion orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.context_fusion.context_priority_engine import prioritize
from odin_backend.core.context_fusion.cross_application_context import merge_contexts
from odin_backend.core.context_fusion.intent_continuity import track_intent
from odin_backend.core.context_fusion.interruption_recovery import recover_interruption
from odin_backend.core.context_fusion.session_fusion import fuse_sessions
from odin_backend.core.context_fusion.temporal_focus_tracker import track_focus
from odin_backend.core.context_fusion.workspace_attention import AttentionGraph


class ContextFusionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._attention = AttentionGraph()
        self._switches = 0

    async def fuse(self, *, ide: dict | None = None, terminal: dict | None = None, browser: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "context_fusion_enabled", False):
            return {"accepted": False, "reason": "context_fusion_disabled"}
        merged = merge_contexts(ide=ide, terminal=terminal, browser=browser)
        fused = fuse_sessions(sources=merged["sources"])
        focus = track_focus(active_app=merged.get("active_app", "unknown"))
        priority = prioritize(context=merged, focus=focus)
        self._attention.update(app=merged.get("active_app", "unknown"), weight=priority["score"])
        intent = track_intent(signals=merged.get("signals", []))
        self._emit("live_context_fused", {"sources": len(merged["sources"]), "intent": intent["intent"]})
        self._emit("active_context_updated", {"app": merged.get("active_app"), "priority": priority["score"]})
        return {"accepted": True, "merged": merged, "fused": fused, "focus": focus, "priority": priority, "intent": intent}

    async def recover(self, *, interrupted: dict) -> dict[str, Any]:
        recovery = recover_interruption(state=interrupted)
        self._emit("interruption_detected", {"recovered": recovery["recovered"]})
        if recovery.get("continuity"):
            self._emit("continuity_restored_live", recovery)
        return {"accepted": True, **recovery}

    def snapshot(self) -> dict[str, Any]:
        return {"attention": self._attention.snapshot(), "switches": self._switches}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="context_fusion")

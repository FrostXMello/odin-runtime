"""Unified cognitive core orchestration (Prompt 52)."""
from __future__ import annotations
from typing import Any


class UnifiedCognitiveCoreRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._objectives: list[str] = []
        self._tick_count = 0

    async def cognition_tick(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "unified_cognitive_core_enabled", False):
            return {"accepted": False, "reason": "unified_cognitive_core_disabled"}
        self._emit("cognition_tick_started", {"tick": self._tick_count})
        if hasattr(self._app, "realtime_cognition"):
            await self._app.realtime_cognition.heartbeat()
        if hasattr(self._app, "attention_engine"):
            await self._app.attention_engine.calculate_attention_weights()
        if hasattr(self._app, "cognitive_state"):
            await self._app.cognitive_state.compute_cognitive_state()
        self._tick_count += 1
        self._emit("cognition_tick_completed", {"tick": self._tick_count})
        return {"accepted": True, "tick": self._tick_count, "no_direct_execution": True}

    async def synchronize_runtimes(self) -> dict[str, Any]:
        if hasattr(self._app, "runtime_coordination"):
            overlap = await self._app.runtime_coordination.detect_runtime_overlap()
            await self._app.runtime_coordination.synchronize_streams()
            return {"accepted": True, "sync": overlap}
        return {"accepted": True, "sync": {"runtimes": []}}

    async def rebuild_context(self) -> dict[str, Any]:
        if hasattr(self._app, "memory_intelligence"):
            await self._app.memory_intelligence.recall_contextual(query="global")
        self._emit("global_context_rebuilt", {"rebuilt": True})
        return {"accepted": True, "rebuilt": True}

    async def update_attention(self, *, focus: str) -> dict[str, Any]:
        if hasattr(self._app, "attention_engine"):
            return await self._app.attention_engine.shift_attention(focus=focus)
        return {"accepted": False, "reason": "attention_engine_unavailable"}

    async def checkpoint_global_state(self) -> dict[str, Any]:
        snap = {
            "objectives": list(self._objectives),
            "tick": self._tick_count,
        }
        if hasattr(self._app, "cognitive_state"):
            snap["cognitive_state"] = (await self._app.cognitive_state.export_state_snapshot()).get("state")
        return {"accepted": True, "checkpoint": snap}

    def snapshot(self) -> dict[str, Any]:
        profile = getattr(self._app.settings, "global_cognition_profile", "balanced")
        return {"tick_count": self._tick_count, "objectives": len(self._objectives), "profile": profile}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="unified_cognitive_core")

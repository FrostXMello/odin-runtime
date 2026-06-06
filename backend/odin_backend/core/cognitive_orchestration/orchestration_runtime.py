"""Cognitive orchestration daemon (Prompt 48)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_orchestration.background_reflection_scheduler import reflect
from odin_backend.core.cognitive_orchestration.cognition_tick_engine import tick
from odin_backend.core.cognitive_orchestration.cross_runtime_synchronizer import sync
from odin_backend.core.cognitive_orchestration.deferred_reasoning_queue import DeferredReasoningQueue
from odin_backend.core.cognitive_orchestration.overnight_cognition import overnight
from odin_backend.core.cognitive_orchestration.resource_balancer import balance
from odin_backend.core.cognitive_orchestration.runtime_attention_loop import loop


class CognitiveOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue = DeferredReasoningQueue()
        self._profile = "balanced"

    async def cognition_tick(self, *, idle_s: float = 0.0) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_orchestration_enabled", False):
            return {"accepted": False, "reason": "cognitive_orchestration_disabled"}
        t = await tick(self._app)
        bal = balance(self._profile)
        attn = loop(profile=self._profile)
        deferred = self._queue.drain()
        synced = await sync(self._app)
        self._emit("cognitive_tick_executed", {"idle_s": idle_s})
        self._emit("cross_runtime_sync_completed", synced)
        return {
            "accepted": True,
            "tick": t,
            "balance": bal,
            "attention_loop": attn,
            "deferred": deferred,
            "sync": synced,
            "resource_aware": True,
        }

    async def overnight_cycle(self) -> dict[str, Any]:
        result = await overnight(self._app)
        ref = await reflect(self._app)
        self._emit("overnight_reflection_completed", {"completed": True})
        return {"accepted": True, "overnight": result, "reflection": ref}

    async def defer(self, *, thought: str) -> dict[str, Any]:
        self._queue.defer(thought)
        return {"accepted": True, "queued": True}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("survival", "lightweight", "balanced", "immersive", "overnight", "cinematic"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile, **balance(profile)}

    def snapshot(self) -> dict[str, Any]:
        return {"profile": self._profile}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_orchestration")

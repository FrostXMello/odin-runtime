"""Adaptive cognitive runtime manager (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.adaptive_runtime.background_optimization_loop import optimize
from odin_backend.core.adaptive_runtime.cognitive_state_controller import intensity
from odin_backend.core.adaptive_runtime.dynamic_attention_router import route
from odin_backend.core.adaptive_runtime.runtime_priority_engine import prioritize


class AdaptiveRuntimeManager:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._profile = "balanced"

    async def scale(self, *, load: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "adaptive_runtime_enabled", False):
            return {"accepted": False, "reason": "adaptive_runtime_disabled"}
        bal = {}
        if hasattr(self._app, "cognitive_load_balancer"):
            bal = await self._app.cognitive_load_balancer.balance(load=load)
        priority = prioritize(load=load)
        attn = route(focus=priority)
        inten = intensity(self._profile)
        self._emit("adaptive_scaling_applied", {"profile": self._profile, "intensity": inten})
        self._emit("runtime_priority_shifted", {"priority": priority})
        caps = {"survival": 10, "balanced": 30, "immersive": 45, "cinematic": 60, "overnight_autonomous": 8}
        return {
            "accepted": True,
            "profile": self._profile,
            "intensity": inten,
            "priority": priority,
            "routing": attn,
            "balance": bal,
            "fps_cap": caps.get(self._profile, 30),
        }

    async def optimize_background(self) -> dict[str, Any]:
        result = await optimize(self._app)
        self._emit("background_optimization_completed", {"completed": True})
        return {"accepted": True, "optimization": result}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("survival", "balanced", "immersive", "cinematic", "overnight_autonomous"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile}

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="adaptive_runtime")

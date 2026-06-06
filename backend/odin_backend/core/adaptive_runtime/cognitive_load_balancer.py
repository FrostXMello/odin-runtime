"""Cognitive load balancer (Prompt 49)."""
from __future__ import annotations
from typing import Any


class CognitiveLoadBalancer:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._load = 0.4

    async def balance(self, *, load: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_load_balancing_enabled", False):
            return {"accepted": False, "reason": "cognitive_load_balancing_disabled"}
        self._load = min(1.0, max(0.0, load))
        throttle = self._load > 0.75
        self._emit("cognition_load_balanced", {"load": self._load, "throttle": throttle})
        return {
            "accepted": True,
            "load": self._load,
            "throttle_streams": throttle,
            "agent_limit": 2 if throttle else 4,
            "lazy_render": throttle,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"load": self._load}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_load_balancer")

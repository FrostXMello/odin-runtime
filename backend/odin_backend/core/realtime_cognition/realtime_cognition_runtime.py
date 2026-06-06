"""Real-time cognitive infrastructure (Prompt 51)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.realtime_cognition.cognitive_heartbeat_engine import beat
from odin_backend.core.realtime_cognition.context_priority_scheduler import schedule
from odin_backend.core.realtime_cognition.continuous_reasoning_runtime import ContinuousReasoningRuntime
from odin_backend.core.realtime_cognition.realtime_awareness_engine import aware


class RealtimeCognitionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._reasoning = ContinuousReasoningRuntime(app)

    async def heartbeat(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "realtime_cognition_enabled", False):
            return {"accepted": False, "reason": "realtime_cognition_disabled"}
        b = await beat(self._app)
        self._emit("cognitive_heartbeat_executed", {"beat": True})
        return {"accepted": True, "heartbeat": b, "continuous": True}

    async def reason(self, *, thought: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "continuous_reasoning_enabled", False):
            return {"accepted": False, "reason": "continuous_reasoning_disabled"}
        r = await self._reasoning.update(thought=thought)
        self._emit("continuous_reasoning_updated", {"thought": thought[:80]})
        if hasattr(self._app, "adaptive_runtime"):
            await self._app.adaptive_runtime.scale(load=0.5)
        return {"accepted": True, **r}

    async def prioritize(self, *, load: float = 0.5) -> dict[str, Any]:
        sched = schedule(load=load)
        aw = aware(context=sched.get("priority", "workspace"))
        return {"accepted": True, "schedule": sched, "awareness": aw}

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="realtime_cognition")

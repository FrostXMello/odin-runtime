"""Continuous cognition orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.continuous_cognition.active_reasoning_loop import reasoning_tick
from odin_backend.core.continuous_cognition.background_synthesis import synthesize_background
from odin_backend.core.continuous_cognition.cognition_scheduler import should_tick
from odin_backend.core.continuous_cognition.cognitive_tick_engine import run_tick
from odin_backend.core.continuous_cognition.continuity_snapshots import snapshot_state
from odin_backend.core.continuous_cognition.deferred_thoughts import DeferredThoughts
from odin_backend.core.continuous_cognition.ongoing_analysis import analyze_ongoing


class ContinuousCognitionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._deferred = DeferredThoughts()
        self._ticks = 0

    async def tick(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "continuous_cognition_enabled", False):
            return {"accepted": False, "reason": "continuous_cognition_disabled"}
        on_battery = getattr(self._app.settings, "on_battery", False)
        if not should_tick(on_battery=on_battery, heavy_load=getattr(self._app.settings, "heavy_load", False)):
            return {"accepted": True, "skipped": True, "reason": "throttled"}
        result = run_tick()
        reasoning = reasoning_tick()
        synthesis = synthesize_background(thoughts=self._deferred.list_all())
        analysis = analyze_ongoing()
        self._ticks += 1
        self._emit("cognition_tick_completed", {"tick": self._ticks, **result})
        return {"accepted": True, "tick": result, "reasoning": reasoning, "synthesis": synthesis, "analysis": analysis}

    async def defer(self, *, thought: str) -> dict[str, Any]:
        entry = self._deferred.add(thought)
        return {"accepted": True, "entry": entry}

    async def checkpoint(self) -> dict[str, Any]:
        state = snapshot_state(ticks=self._ticks, deferred=len(self._deferred.list_all()))
        return {"accepted": True, **state}

    def snapshot(self) -> dict[str, Any]:
        return {"ticks": self._ticks, "deferred": len(self._deferred.list_all())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="continuous_cognition")

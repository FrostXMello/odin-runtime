"""Cognitive daemon V2 extensions (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_daemon.deferred_reasoning_store import defer, restore
from odin_backend.core.cognitive_daemon.low_power_mode import transition
from odin_backend.core.cognitive_daemon.memory_consolidation import consolidate
from odin_backend.core.cognitive_daemon.overnight_cycles import run


class CognitiveDaemonV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._path = "./data/deferred_reasoning.json"
        self._low_power = False

    async def overnight(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_daemon_v2_enabled", False):
            return {"accepted": False, "reason": "cognitive_daemon_v2_disabled"}
        cycle = await run(self._app)
        mem = await consolidate(self._app)
        self._emit("overnight_cycle_completed", {"completed": True})
        self._emit("overnight_optimization_completed", {"completed": True})
        return {"accepted": True, "cycle": cycle, "memory": mem}

    async def defer_thought(self, *, thought: str) -> dict[str, Any]:
        defer(path=self._path, thought=thought)
        return {"accepted": True, "deferred": True}

    async def restore_deferred(self) -> dict[str, Any]:
        r = restore(path=self._path)
        if r.get("restored"):
            self._emit("deferred_reasoning_restored", {"count": len(r.get("thoughts", []))})
        return {"accepted": True, **r}

    async def resume_cognition(self) -> dict[str, Any]:
        restored = await self.restore_deferred()
        if hasattr(self._app, "cognitive_daemon"):
            await self._app.cognitive_daemon.tick(idle_s=0)
        self._emit("cognitive_resume_completed", {"resumed": True})
        return {"accepted": True, "restored": restored}

    async def set_low_power(self, *, enabled: bool = True) -> dict[str, Any]:
        self._low_power = enabled
        t = transition(enabled=enabled)
        self._emit("low_power_transition", t)
        return {"accepted": True, **t}

    def snapshot(self) -> dict[str, Any]:
        return {"low_power": self._low_power}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_daemon_v2")

"""Background cognitive infrastructure orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.background_cognition.contradiction_review import review_contradictions
from odin_backend.core.background_cognition.dormant_objective_review import review_dormant
from odin_backend.core.background_cognition.idle_reasoning import idle_reason
from odin_backend.core.background_cognition.memory_consolidation import MemoryConsolidation
from odin_backend.core.background_cognition.optimization_cycles import OptimizationCycles
from odin_backend.core.background_cognition.reflection_scheduler import ReflectionScheduler
from odin_backend.core.background_cognition.retrospective_analysis import analyze_failures
from odin_backend.core.background_cognition.strategy_refinement import refine_strategies


class BackgroundCognitionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._consolidation = MemoryConsolidation()
        self._scheduler = ReflectionScheduler()
        self._cycles = OptimizationCycles()
        self._last_run: dict[str, Any] | None = None

    async def run_cycle(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "background_cognition_enabled", False):
            return {"accepted": False, "reason": "background_cognition_disabled"}
        consolidated = self._consolidation.run()
        self._emit("memory_consolidated", consolidated)
        idle = idle_reason(topic="idle_review")
        retro = analyze_failures([])
        refine = refine_strategies(["routing", "planning"])
        contra = review_contradictions([])
        dormant = review_dormant([])
        if hasattr(self._app, "agent_society"):
            objs = await self._app.agent_society._objectives.list_all()
            dormant = review_dormant(objs)
        cycle = self._cycles.run()
        self._last_run = {
            "consolidation": consolidated,
            "idle": idle,
            "retrospective": retro,
            "refinement": refine,
            "contradictions": contra,
            "dormant": dormant,
            "cycle": cycle,
        }
        return {"accepted": True, "result": self._last_run}

    def snapshot(self) -> dict[str, Any]:
        return {
            "last_run": self._last_run,
            "pending_reflections": len(self._scheduler.pending()),
            "consolidation_history": len(self._consolidation.history()),
        }

    def cancel(self) -> dict[str, Any]:
        cancelled = self._scheduler.cancel_all()
        return {"cancelled": cancelled}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="background_cognition")

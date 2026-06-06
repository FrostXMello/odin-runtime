"""Autonomous engineering director V2 (Prompt 50)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.engineering_evolution_v2.multi_repo_reasoner import reason
from odin_backend.core.engineering_evolution_v2.patch_evaluation_runtime import PatchEvaluationRuntime
from odin_backend.core.engineering_evolution_v2.refactor_simulation_runtime import RefactorSimulationRuntime
from odin_backend.core.engineering_evolution_v2.regression_forecast_runtime import RegressionForecastRuntime


class AutonomousEngineeringDirector:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._patches = PatchEvaluationRuntime(app)
        self._refactor = RefactorSimulationRuntime(app)
        self._forecast = RegressionForecastRuntime(app)

    async def analyze_multi_repo(self, *, repos: list[str]) -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_evolution_v2_enabled", False):
            return {"accepted": False, "reason": "engineering_evolution_v2_disabled"}
        result = reason(repos=repos)
        self._emit("multi_repo_reasoning_completed", result)
        return {"accepted": True, "reasoning": result, "supervised": True}

    async def evaluate_patch(self, *, patch: str) -> dict[str, Any]:
        return await self._patches.evaluate(patch=patch)

    async def simulate_refactor(self, *, scope: str) -> dict[str, Any]:
        return await self._refactor.simulate(scope=scope)

    async def forecast_regression(self, *, change: str) -> dict[str, Any]:
        return await self._forecast.forecast(change=change)

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="engineering_evolution_v2")

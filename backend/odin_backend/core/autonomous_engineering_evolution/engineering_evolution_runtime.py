"""Autonomous engineering evolution (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.autonomous_engineering_evolution.patch_simulation_engine import simulate
from odin_backend.core.autonomous_engineering_evolution.refactor_opportunity_detector import detect
from odin_backend.core.autonomous_engineering_evolution.repo_evolution_analyzer import analyze
from odin_backend.core.autonomous_engineering_evolution.technical_debt_predictor import predict_debt
from odin_backend.core.autonomous_engineering_evolution.upgrade_planning_runtime import UpgradePlanningRuntime


class EngineeringEvolutionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._planner = UpgradePlanningRuntime(app)

    async def analyze_repo(self, *, repo: str = "local") -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_evolution_enabled", False):
            return {"accepted": False, "reason": "engineering_evolution_disabled"}
        evo = analyze(repo=repo)
        debt = predict_debt(churn=24)
        if debt.get("debt_likely"):
            self._emit("technical_debt_detected", debt)
        refs = detect(files=[f"{repo}/core", f"{repo}/api"])
        return {"accepted": True, "evolution": evo, "debt": debt, "refactors": refs, "supervised": True}

    async def simulate_patch(self, *, patch: str) -> dict[str, Any]:
        sim = simulate(patch=patch)
        if hasattr(self._app, "self_improvement_sandbox"):
            await self._app.self_improvement_sandbox.experiment(name="patch-sim")
        return {"accepted": True, **sim}

    async def propose_upgrade(self, *, goal: str) -> dict[str, Any]:
        return await self._planner.plan(goal=goal)

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="engineering_evolution")

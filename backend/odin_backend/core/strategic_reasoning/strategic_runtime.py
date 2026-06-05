"""Strategic reasoning runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.strategic_reasoning.economic_reasoning import balance_resources
from odin_backend.core.strategic_reasoning.geopolitical_reasoning import assess_scenario
from odin_backend.core.strategic_reasoning.long_horizon_objectives import LongHorizonObjectives
from odin_backend.core.strategic_reasoning.organizational_reasoning import analyze_organization
from odin_backend.core.strategic_reasoning.recursive_planning import recursive_plan
from odin_backend.core.strategic_reasoning.risk_projection import project_risk
from odin_backend.core.strategic_reasoning.systems_reasoning import analyze_system


class StrategicReasoningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._objectives = LongHorizonObjectives()
        self._analyses: list[dict[str, Any]] = []

    async def analyze(self, *, goal: str, context: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "strategic_reasoning_enabled", False):
            return {"accepted": False, "reason": "strategic_reasoning_disabled"}
        ctx = context or {}
        plan = recursive_plan(goal, depth=ctx.get("depth", 3))
        resources = balance_resources(ctx.get("resources", {"compute": 1.0, "memory": 0.5}))
        risk = project_risk(likelihood=ctx.get("likelihood", 0.3), impact=ctx.get("impact", 0.5))
        org = analyze_organization(ctx.get("roles", ["planner", "executor"]))
        systems = analyze_system(ctx.get("components", ["runtime"]), ctx.get("dependencies", []))
        refs = []
        if hasattr(self._app, "knowledge_runtime"):
            nodes = await self._app.knowledge_runtime.list_knowledge(limit=5)
            refs = [n.get("fact", "")[:60] for n in nodes]
        result = {
            "goal": goal,
            "plan": plan,
            "resources": resources,
            "risk": risk,
            "organization": org,
            "systems": systems,
            "assumptions": ["local_first", "operator_supervised", "no_hidden_execution"],
            "uncertainty": risk["uncertainty"],
            "confidence": round(1.0 - risk["uncertainty"], 4),
            "causal_justification": f"multi_factor_analysis_for_{goal}",
            "knowledge_references": refs,
        }
        self._analyses.append(result)
        self._emit("strategy_generated", {"goal": goal, "confidence": result["confidence"]})
        return {"accepted": True, "analysis": result}

    def create_objective(self, *, title: str, horizon_days: int = 30) -> dict[str, Any]:
        return self._objectives.create(title=title, horizon_days=horizon_days)

    def assess_geopolitical(self, *, region: str, factors: list[str]) -> dict[str, Any]:
        return assess_scenario(region, factors)

    def snapshot(self) -> dict[str, Any]:
        return {
            "objectives": self._objectives.list_all(),
            "recent_analyses": self._analyses[-5:],
        }

    def analysis_for_mission(self, mission_id: str) -> list[dict[str, Any]]:
        return [a for a in self._analyses if a.get("mission_id") == mission_id]

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="strategic_reasoning")

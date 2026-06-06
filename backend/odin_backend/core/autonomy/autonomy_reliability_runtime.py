"""Autonomous task reliability runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agent_society.society_intelligence import (
    distill_reasoning,
    route_expertise,
    score_consensus,
    score_delegation,
)
from odin_backend.core.autonomy.task_reliability import (
    analyze_execution_risk,
    estimate_viability,
    objective_stability,
    plan_rollback,
    select_retry_strategy,
)


class AutonomyReliabilityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def assess_task(self, *, complexity: float, action: str, destructive: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomy_reliability_enabled", False):
            return {"accepted": False, "reason": "autonomy_reliability_disabled"}
        viability = estimate_viability(complexity=complexity, resources_ok=True, approvals=not destructive)
        risk = analyze_execution_risk(action=action, destructive=destructive)
        delegation = score_delegation(task_complexity=complexity, agent_fit=0.7)
        if delegation["recommended"]:
            self._emit("delegation_optimized", delegation)
        return {"accepted": True, "viability": viability, "risk": risk, "delegation": delegation}

    async def retry_plan(self, *, error: str, retries: int = 0) -> dict[str, Any]:
        strategy = select_retry_strategy(error=error, retries=retries)
        self._emit("retry_strategy_selected", strategy)
        return {"accepted": True, **strategy}

    async def society_route(self, *, task: str, experts: dict[str, float] | None = None) -> dict[str, Any]:
        experts = experts or {"generalist": 0.5, "coder": 0.8, "researcher": 0.6}
        routed = route_expertise(task=task, experts=experts)
        consensus = score_consensus(votes=list(experts.values()))
        distilled = distill_reasoning(patterns=[task])
        return {"accepted": True, "route": routed, "consensus": consensus, "distilled": distilled}

    async def rollback(self, *, steps: list[str]) -> dict[str, Any]:
        return {"accepted": True, **plan_rollback(steps=steps)}

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": getattr(self._app.settings, "autonomy_reliability_enabled", False)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomy_reliability")

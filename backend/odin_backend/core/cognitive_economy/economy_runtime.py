"""Cognitive economy orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognitive_economy.cognition_budgeting import CognitionBudgeting
from odin_backend.core.cognitive_economy.compute_allocator import allocate
from odin_backend.core.cognitive_economy.mission_valuation import value_mission
from odin_backend.core.cognitive_economy.model_cost_balancer import select_model
from odin_backend.core.cognitive_economy.reasoning_priority import priority_score
from odin_backend.core.cognitive_economy.resource_negotiation import negotiate
from odin_backend.core.cognitive_economy.token_economy import TokenEconomy


class CognitiveEconomyRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        mode = getattr(app.settings, "cognitive_economy_mode", "balanced")
        self._budget = CognitionBudgeting(mode=mode)
        self._tokens = TokenEconomy()

    def charge(self, *, mission_id: str | None, tokens: int, model: str = "mock") -> dict[str, Any]:
        ok, reason = self._budget.spend(tokens)
        if not ok:
            return {"accepted": False, "reason": reason}
        entry = self._tokens.charge(mission_id=mission_id, tokens=tokens, model=model)
        self._emit("cognition_budget_updated", self._budget.snapshot())
        return {"accepted": True, "charge": entry}

    def set_mode(self, mode: str) -> dict[str, Any]:
        self._budget.set_mode(mode)
        return self._budget.snapshot()

    def mission_economy(self, mission_id: str) -> dict[str, Any]:
        tokens = self._tokens.total_for_mission(mission_id)
        valuation = value_mission(priority="medium", complexity=0.5)
        return {"mission_id": mission_id, "tokens": tokens, "valuation": valuation}

    def snapshot(self) -> dict[str, Any]:
        model = select_model(mode=self._budget._mode, task_complexity=0.5)
        alloc = allocate(available=100.0, demands=[30, 40, 30])
        return {
            "budget": self._budget.snapshot(),
            "selected_model": model,
            "allocation": alloc,
            "priority_example": priority_score(urgency=0.8, value=0.7, cost=0.3),
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_economy")

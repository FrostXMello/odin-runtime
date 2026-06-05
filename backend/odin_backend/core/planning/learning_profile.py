"""Planner learning profile — aggregated strategy performance."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PlannerLearningProfile(BaseModel):
    strategy_success_rate: dict[str, float] = Field(default_factory=dict)
    retry_rate: float = 0.0
    validation_pass_rate: float = 0.75
    avg_execution_cost: float = 0.0
    avg_latency_ms: float = 0.0
    recovery_probability: float = 0.5
    penalized_capabilities: list[str] = Field(default_factory=list)
    preferred_tools: dict[str, str] = Field(default_factory=dict)

    @property
    def best_strategy(self) -> str | None:
        if not self.strategy_success_rate:
            return None
        return max(self.strategy_success_rate, key=self.strategy_success_rate.get)

"""Strategy optimization from historical performance."""

from __future__ import annotations

from typing import Any

from odin_backend.core.planning.execution_strategy import ExecutionStrategy, StrategyKind, select_strategy
from odin_backend.core.planning.learning_profile import PlannerLearningProfile
from odin_backend.core.planning.objectives import ParsedObjective


def optimize_strategy(
    parsed: ParsedObjective,
    profile: PlannerLearningProfile,
    *,
    sandbox_only: bool = False,
    autonomy_level: int = 1,
) -> ExecutionStrategy:
    base = select_strategy(parsed, sandbox_only=sandbox_only, autonomy_level=autonomy_level)
    override = None
    if profile.best_strategy:
        try:
            override = StrategyKind(profile.best_strategy)
        except ValueError:
            override = None
    if override and profile.strategy_success_rate.get(override.value, 0) >= 0.6:
        return ExecutionStrategy(
            kind=override,
            rationale=f"learned preference for {override.value}",
            metadata={"learned": True},
        )
    return base

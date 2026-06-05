"""Execution strategy selection."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.planning.objectives import ParsedObjective


class StrategyKind(StrEnum):
    SEQUENTIAL = "sequential"
    PARALLEL_WAVES = "parallel_waves"
    VALIDATE_THEN_EXECUTE = "validate_then_execute"
    RESEARCH_FIRST = "research_first"
    ITERATIVE = "iterative"
    SANDBOX_ONLY = "sandbox_only"


class ExecutionStrategy(BaseModel):
    kind: StrategyKind = StrategyKind.SEQUENTIAL
    parallelizable: bool = False
    staged: bool = False
    validation_first: bool = False
    deferred_subtasks: bool = False
    checkpoint_interval: int = 1
    rationale: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


def select_strategy(
    parsed: ParsedObjective,
    *,
    sandbox_only: bool = False,
    autonomy_level: int = 1,
) -> ExecutionStrategy:
    if sandbox_only:
        return ExecutionStrategy(
            kind=StrategyKind.SANDBOX_ONLY,
            rationale="policy requires sandbox execution",
        )

    if parsed.intent == "research" or parsed.domain == "research":
        return ExecutionStrategy(
            kind=StrategyKind.RESEARCH_FIRST,
            validation_first=True,
            staged=True,
            rationale="research objectives benefit from gather-then-execute",
        )

    if "requires_validation" in parsed.constraints or "validate" in parsed.verbs:
        return ExecutionStrategy(
            kind=StrategyKind.VALIDATE_THEN_EXECUTE,
            validation_first=True,
            staged=True,
            rationale="objective explicitly requires validation",
        )

    if "parallelizable" in parsed.constraints or parsed.intent == "multi_step":
        return ExecutionStrategy(
            kind=StrategyKind.PARALLEL_WAVES,
            parallelizable=True,
            staged=True,
            checkpoint_interval=2,
            rationale="multi-step objective with parallel waves",
        )

    if autonomy_level >= 4 and len(parsed.verbs) > 2:
        return ExecutionStrategy(
            kind=StrategyKind.ITERATIVE,
            staged=True,
            deferred_subtasks=True,
            checkpoint_interval=1,
            rationale="high autonomy long-horizon iterative refinement",
        )

    return ExecutionStrategy(
        kind=StrategyKind.SEQUENTIAL,
        rationale="default sequential execution",
    )

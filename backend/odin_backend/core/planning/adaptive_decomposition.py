"""Adaptive decomposition using memory-guided hints."""

from __future__ import annotations

from typing import Any

from odin_backend.core.planning.decomposition import (
    DecomposedStep,
    decompose_objective,
    infer_capability,
    infer_tool,
)
from odin_backend.core.planning.execution_strategy import ExecutionStrategy
from odin_backend.core.planning.learning_profile import PlannerLearningProfile
from odin_backend.core.planning.objectives import ParsedObjective


def adapt_steps(
    steps: list[DecomposedStep],
    profile: PlannerLearningProfile,
    *,
    memory_hints: list[dict[str, Any]] | None = None,
) -> list[DecomposedStep]:
    penalized = set(profile.penalized_capabilities)
    adapted: list[DecomposedStep] = []
    for step in steps:
        if step.capability in penalized:
            alt = infer_capability(ParsedObjective(raw=step.goal, intent="execute"), step.goal)
            if alt.capability not in penalized:
                step = DecomposedStep(
                    goal=step.goal,
                    capability=alt.capability,
                    tool=infer_tool(alt.capability),
                    params=step.params,
                    confidence=max(0.3, step.confidence - 0.15),
                    blocking=step.blocking,
                    parallelizable=step.parallelizable,
                    step_kind=step.step_kind,
                )
            else:
                step = DecomposedStep(
                    goal=step.goal,
                    capability=step.capability,
                    tool=step.tool,
                    params=step.params,
                    confidence=max(0.3, step.confidence - 0.2),
                    blocking=step.blocking,
                    parallelizable=step.parallelizable,
                    step_kind=step.step_kind,
                )
        if memory_hints:
            for hint in memory_hints:
                if hint.get("confidence", 0) >= 0.65 and hint.get("metadata"):
                    meta = hint.get("metadata") or {}
                    if isinstance(meta, str):
                        import json

                        try:
                            meta = json.loads(meta)
                        except Exception:
                            meta = {}
                    if meta.get("capability") and meta.get("success"):
                        step.confidence = min(0.99, step.confidence + 0.05)
        adapted.append(step)
    return adapted


def decompose_with_learning(
    parsed: ParsedObjective,
    strategy: ExecutionStrategy,
    profile: PlannerLearningProfile,
    *,
    mission_id: str | None = None,
    memory_hints: list[dict[str, Any]] | None = None,
) -> list[DecomposedStep]:
    steps = decompose_objective(parsed, strategy, mission_id=mission_id)
    return adapt_steps(steps, profile, memory_hints=memory_hints)

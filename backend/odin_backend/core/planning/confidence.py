"""Planner confidence propagation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlannerConfidenceProfile:
    plan: float = 0.75
    task: float = 0.75
    tool: float = 0.75
    dependency: float = 0.8
    recovery: float = 0.7

    def to_dict(self) -> dict[str, float]:
        return {
            "plan": self.plan,
            "task": self.task,
            "tool": self.tool,
            "dependency": self.dependency,
            "recovery": self.recovery,
        }

    @property
    def aggregate(self) -> float:
        return (
            self.plan * 0.3
            + self.task * 0.25
            + self.tool * 0.2
            + self.dependency * 0.15
            + self.recovery * 0.1
        )

    def apply_penalty(self, *, reason: str, amount: float = 0.1) -> None:
        self.plan = max(0.05, self.plan - amount)
        self.task = max(0.05, self.task - amount * 0.8)
        if reason in ("tool_ambiguous", "validation_required"):
            self.tool = max(0.05, self.tool - amount)

    def boost(self, *, reason: str, amount: float = 0.05) -> None:
        cap = 0.99
        if reason == "memory_hit":
            self.plan = min(cap, self.plan + amount)
            self.recovery = min(cap, self.recovery + amount * 0.5)
        elif reason == "prior_success":
            self.task = min(cap, self.task + amount)


def compute_plan_confidence(
    *,
    step_count: int,
    has_validation: bool,
    memory_hits: int = 0,
    prior_failures: int = 0,
    tool_ambiguity: float = 0.0,
) -> PlannerConfidenceProfile:
    profile = PlannerConfidenceProfile()
    if step_count > 5:
        profile.plan -= min(0.25, (step_count - 5) * 0.03)
    if has_validation:
        profile.recovery += 0.05
    if memory_hits:
        profile.boost(reason="memory_hit", amount=min(0.15, memory_hits * 0.03))
    if prior_failures:
        profile.apply_penalty(reason="prior_failures", amount=min(0.3, prior_failures * 0.08))
    if tool_ambiguity > 0.3:
        profile.apply_penalty(reason="tool_ambiguous", amount=tool_ambiguity * 0.2)
    for k in ("plan", "task", "tool", "dependency", "recovery"):
        v = getattr(profile, k)
        setattr(profile, k, max(0.05, min(0.99, v)))
    return profile


def confidence_action(profile: PlannerConfidenceProfile) -> dict[str, Any]:
    agg = profile.aggregate
    if agg < 0.35:
        return {"batch_size": 1, "validation_checkpoints": 3, "observability": "high"}
    if agg < 0.55:
        return {"batch_size": 2, "validation_checkpoints": 2, "observability": "elevated"}
    return {"batch_size": 4, "validation_checkpoints": 1, "observability": "normal"}

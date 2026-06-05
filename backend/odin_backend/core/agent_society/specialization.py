"""Adaptive specialization with bounded growth."""

from __future__ import annotations

from odin_backend.core.agent_society.personality_bounds import bounded_update

_SPECIALIZATIONS = (
    "planning_specialist",
    "infrastructure_optimizer",
    "research_analyst",
    "failure_diagnostician",
    "execution_strategist",
    "memory_curator",
)


def evolve_expertise(current: float, *, success: bool, domain: str) -> tuple[float, str | None]:
    delta = 0.08 if success else -0.05
    updated = bounded_update(current, delta)
    label = None
    if updated >= 0.75 and domain in _SPECIALIZATIONS:
        label = domain
    elif updated >= 0.7:
        label = domain
    return updated, label


def rebalance(confidence: float) -> float:
    return bounded_update(confidence, -0.02)

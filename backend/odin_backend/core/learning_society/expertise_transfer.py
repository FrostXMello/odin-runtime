"""Transfer expertise between agents."""

from __future__ import annotations

from odin_backend.core.agent_society.personality_bounds import bounded_update


def transfer(*, mentor_confidence: float, mentee_confidence: float, amount: float = 0.05) -> float:
    return bounded_update(mentee_confidence, min(amount, mentor_confidence * 0.1))

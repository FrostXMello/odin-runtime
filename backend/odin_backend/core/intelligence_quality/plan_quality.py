"""Validate generated plans."""

from __future__ import annotations

from typing import Any


def score_plan(*, steps: list[dict[str, Any]], constraints: list[str] | None = None) -> dict[str, Any]:
    constraints = constraints or []
    if not steps:
        return {"score": 0.0, "valid": False, "reason": "empty_plan"}
    has_actions = all(s.get("action") for s in steps)
    bounded = all(s.get("risk", "low") != "critical" for s in steps)
    constraint_ok = len(steps) <= 20
    score = round(0.4 + (0.3 if has_actions else 0) + (0.2 if bounded else 0) + (0.1 if constraint_ok else 0), 3)
    return {"score": score, "valid": has_actions and bounded, "step_count": len(steps)}

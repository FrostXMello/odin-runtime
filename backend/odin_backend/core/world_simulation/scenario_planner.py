"""Scenario planning for world simulation."""

from __future__ import annotations

from typing import Any


def plan_scenarios(goal: str, *, horizon_steps: int = 3) -> list[dict[str, Any]]:
    steps = min(horizon_steps, 10)
    return [
        {"step": i + 1, "action": f"advance_{goal}_step_{i+1}", "confidence": round(0.85 - i * 0.08, 2)}
        for i in range(steps)
    ]

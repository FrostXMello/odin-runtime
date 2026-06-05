"""Operational sustainability analysis."""

from __future__ import annotations

from typing import Any


def assess(*, load: float, budget_remaining: float) -> dict[str, Any]:
    sustainable = budget_remaining > load * 10
    return {"sustainable": sustainable, "load": load, "budget_remaining": budget_remaining}

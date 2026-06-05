"""Planner accuracy benchmarks."""

from __future__ import annotations

from typing import Any


def score_planner(*, planned: int, succeeded: int) -> dict[str, Any]:
    rate = succeeded / max(planned, 1)
    return {"accuracy": round(rate, 4), "planned": planned, "succeeded": succeeded}

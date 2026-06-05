"""Objective forecasting."""

from __future__ import annotations

from typing import Any


def forecast(*, objectives: int, horizon_weeks: int) -> dict[str, Any]:
    return {"objectives": objectives, "horizon_weeks": horizon_weeks, "completion_estimate": round(objectives / max(horizon_weeks, 1), 2)}

"""Per-mission cost analysis."""

from __future__ import annotations

from typing import Any


def analyze_mission_cost(*, mission_id: str, tokens: int, duration_s: float) -> dict[str, Any]:
    return {"mission_id": mission_id, "tokens": tokens, "duration_s": duration_s, "cost_score": round(tokens * duration_s / 1000, 4)}

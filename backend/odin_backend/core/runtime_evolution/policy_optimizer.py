"""Bounded policy weight optimization (no code modification)."""

from __future__ import annotations

from typing import Any


def optimize_policy(weights: dict[str, float], *, success_rate: float) -> dict[str, Any]:
    adjusted = {k: min(1.0, max(0.1, v + (success_rate - 0.5) * 0.05)) for k, v in weights.items()}
    return {"weights": adjusted, "delta_bounded": True, "max_delta": 0.05}

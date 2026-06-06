"""Memory pressure management."""

from __future__ import annotations

from typing import Any


def pressure_action(level: str) -> dict[str, Any]:
    if level == "critical":
        return {"evict_models": True, "reduce_workers": True, "throttle": 0.3}
    if level == "high":
        return {"evict_models": True, "reduce_workers": False, "throttle": 0.6}
    return {"evict_models": False, "reduce_workers": False, "throttle": 1.0}

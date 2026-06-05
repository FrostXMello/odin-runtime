"""Execution regression detection."""

from __future__ import annotations

from typing import Any


def detect_regression(
    current: dict[str, float],
    baseline: dict[str, float],
    *,
    min_delta: float = 0.15,
) -> list[dict[str, Any]]:
    regressions: list[dict[str, Any]] = []
    for key, base_val in baseline.items():
        cur = current.get(key, base_val)
        if key.endswith("_rate") or key == "failure_rate":
            if cur - base_val >= min_delta:
                regressions.append({"metric": key, "baseline": base_val, "current": cur})
        elif key in ("success_rate", "reliability", "confidence"):
            if base_val - cur >= min_delta:
                regressions.append({"metric": key, "baseline": base_val, "current": cur})
    return regressions

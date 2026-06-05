"""Regression detection against baseline."""

from __future__ import annotations

from typing import Any


def detect_regression(*, baseline: float, current: float, threshold: float = 0.1) -> dict[str, Any]:
    delta = baseline - current
    return {"regression": delta > threshold, "delta": round(delta, 4), "baseline": baseline, "current": current}

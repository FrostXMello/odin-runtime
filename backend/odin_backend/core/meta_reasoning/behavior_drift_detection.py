"""Behavioral drift detection."""

from __future__ import annotations

from typing import Any


def detect_drift(*, baseline: float, current: float, threshold: float = 0.15) -> dict[str, Any]:
    delta = abs(current - baseline)
    return {"drift_detected": delta > threshold, "delta": round(delta, 4), "threshold": threshold}

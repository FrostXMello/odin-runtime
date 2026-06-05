"""Self-analysis of reasoning quality."""

from __future__ import annotations

from typing import Any


def analyze_quality(*, confidence: float, evidence_count: int) -> dict[str, Any]:
    calibration = min(1.0, evidence_count * 0.15) * confidence
    return {
        "calibration_quality": round(calibration, 4),
        "uncertainty": round(1.0 - calibration, 4),
        "evidence_count": evidence_count,
    }

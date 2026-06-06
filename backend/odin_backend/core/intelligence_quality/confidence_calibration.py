"""Calibrate confidence scores."""

from __future__ import annotations

from typing import Any


def calibrate(*, raw_confidence: float, quality_score: float, risk: float) -> dict[str, Any]:
    adjusted = max(0.0, min(1.0, raw_confidence * 0.5 + quality_score * 0.35 - risk * 0.15))
    return {
        "raw": round(raw_confidence, 3),
        "adjusted": round(adjusted, 3),
        "low_confidence": adjusted < 0.45,
    }

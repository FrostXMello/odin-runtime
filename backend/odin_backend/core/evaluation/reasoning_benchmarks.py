"""Reasoning quality benchmarks."""

from __future__ import annotations

from typing import Any


def score_reasoning(*, confidence: float, evidence: int) -> dict[str, Any]:
    return {"score": round(confidence * min(1.0, evidence * 0.2), 4), "confidence": confidence}

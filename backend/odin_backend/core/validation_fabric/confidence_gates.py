from __future__ import annotations

from typing import Any


def check_confidence_gate(*, confidence: float, min_confidence: float) -> dict[str, Any]:
    passed = confidence >= min_confidence
    return {"passed": passed, "confidence": confidence, "min": min_confidence}

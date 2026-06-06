from __future__ import annotations


def gate(*, confidence: float) -> dict:
    return {"allowed": confidence >= 0.55, "confidence": confidence, "supervised": True}

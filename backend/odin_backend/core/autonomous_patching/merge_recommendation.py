from __future__ import annotations

def recommend(*, confidence: float, regression: bool) -> dict:
    if regression:
        return {"recommend": "rollback", "confidence": confidence, "approval_required": True}
    if confidence >= 0.8:
        return {"recommend": "supervised_merge", "confidence": confidence, "approval_required": True}
    return {"recommend": "hold", "confidence": confidence, "approval_required": True}

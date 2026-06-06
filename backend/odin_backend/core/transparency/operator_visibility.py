from __future__ import annotations

def visibility(*, confidence: float, reason: str) -> dict:
    return {"confidence": round(confidence, 3), "reason": reason[:200], "override_allowed": True}

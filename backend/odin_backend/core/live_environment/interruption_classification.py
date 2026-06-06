from __future__ import annotations

def classify(*, reason: str) -> dict:
    urgent = reason in ("error", "mission", "approval")
    return {"reason": reason, "urgent": urgent, "class": "urgent" if urgent else "deferrable"}

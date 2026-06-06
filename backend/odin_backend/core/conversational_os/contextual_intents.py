from __future__ import annotations

def intent(*, workspace: dict | None = None) -> dict:
    ws = workspace or {}
    if ws.get("debugging"):
        return {"intent": "debugging", "confidence": 0.85}
    return {"intent": "general", "confidence": 0.6}

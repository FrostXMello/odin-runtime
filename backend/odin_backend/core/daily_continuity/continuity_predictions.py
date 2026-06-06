from __future__ import annotations

def predict(*, last_action: str) -> dict:
    nxt = "continue debugging" if "debug" in last_action.lower() else "resume project"
    return {"next": nxt, "confidence": 0.7}

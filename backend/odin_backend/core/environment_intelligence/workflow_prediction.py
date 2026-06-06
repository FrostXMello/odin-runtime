from __future__ import annotations


def predict(*, intent: str) -> dict:
    return {"next_action": f"continue {intent[:40]}", "confidence": 0.65}

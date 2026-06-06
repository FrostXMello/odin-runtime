from __future__ import annotations


def predict(*, history: list[str]) -> dict:
    nxt = history[-1] if history else "resume engineering"
    return {"next_task": nxt, "confidence": 0.62}

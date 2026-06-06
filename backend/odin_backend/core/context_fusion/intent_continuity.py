from __future__ import annotations

from typing import Any


def track_intent(*, signals: list[str]) -> dict[str, Any]:
    if "debugging" in signals:
        return {"intent": "debugging", "confidence": 0.75}
    if "terminal_active" in signals:
        return {"intent": "engineering", "confidence": 0.65}
    return {"intent": "general", "confidence": 0.4}

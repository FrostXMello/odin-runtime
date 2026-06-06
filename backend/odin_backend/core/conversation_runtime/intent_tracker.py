"""Multi-turn intent tracking."""
from __future__ import annotations
from typing import Any

def track_intent(*, turns: list[str]) -> dict[str, Any]:
    joined = " ".join(turns[-3:]).lower()
    if "debug" in joined:
        return {"intent": "debugging", "confidence": 0.8}
    if "research" in joined:
        return {"intent": "research", "confidence": 0.75}
    return {"intent": "general", "confidence": 0.6}

"""Operator intent detection."""

from __future__ import annotations

from typing import Any


def detect_intent(actions: list[str]) -> dict[str, Any]:
    if not actions:
        return {"intent": "idle", "confidence": 0.5}
    if any("debug" in a for a in actions):
        return {"intent": "debugging", "confidence": 0.75}
    if any("search" in a for a in actions):
        return {"intent": "research", "confidence": 0.7}
    return {"intent": "general_work", "confidence": 0.6}

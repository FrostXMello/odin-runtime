"""Voice emotion estimation stub."""

from __future__ import annotations

from typing import Any


def estimate_tone(text: str) -> dict[str, Any]:
    lower = text.lower()
    if any(w in lower for w in ("urgent", "help", "error")):
        return {"tone": "concerned", "confidence": 0.6}
    return {"tone": "neutral", "confidence": 0.7}

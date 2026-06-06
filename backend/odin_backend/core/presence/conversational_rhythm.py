"""Conversational pacing."""
from __future__ import annotations

def rhythm(*, wpm: float = 140.0) -> dict[str, float]:
    return {"wpm": wpm, "pause_ms": 250 if wpm > 160 else 400}

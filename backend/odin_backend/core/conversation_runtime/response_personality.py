"""Adaptive conversational tone."""
from __future__ import annotations
from typing import Any

def tone_for_mode(mode: str) -> dict[str, Any]:
    tones = {
        "engineering": {"style": "precise", "verbosity": "medium"},
        "debugging": {"style": "diagnostic", "verbosity": "high"},
        "reflective": {"style": "calm", "verbosity": "low"},
    }
    return tones.get(mode, {"style": "helpful", "verbosity": "medium"})

"""Cognitive presence state for unified shell."""

from __future__ import annotations

from typing import Any


def compute_presence(*, active: bool, focus: str, energy: float) -> dict[str, Any]:
    state = "active" if active else "idle"
    if energy > 0.7:
        state = "engaged"
    return {
        "state": state,
        "focus": focus,
        "energy": round(min(1.0, max(0.0, energy)), 3),
        "visible": True,
        "simulated": True,
    }

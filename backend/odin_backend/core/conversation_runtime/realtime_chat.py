"""Streaming chat primitives."""
from __future__ import annotations
from typing import Any

MODES = ("assistant", "engineering", "research", "strategic", "debugging", "copilot", "reflective")

def start_turn(*, mode: str = "assistant", prompt: str = "") -> dict[str, Any]:
    m = mode if mode in MODES else "assistant"
    return {"mode": m, "prompt": prompt[:2000], "streaming": True}

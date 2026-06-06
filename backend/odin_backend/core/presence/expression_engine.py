"""Visual expression metadata."""
from __future__ import annotations
from typing import Any

def expression_for(mood: str) -> dict[str, Any]:
    palette = {"focused": "#60a5fa", "calm": "#94a3b8", "neutral": "#cbd5e1"}
    return {"color": palette.get(mood, "#cbd5e1"), "animation": "pulse" if mood == "focused" else "idle"}

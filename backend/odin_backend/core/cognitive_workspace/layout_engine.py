from __future__ import annotations
from typing import Any

DEFAULT_PANELS = [
    "chat", "thought_stream", "reasoning", "missions", "agents",
    "memory_timeline", "voice_dock", "command_palette",
]


def build_layout(*, mode: str, panels: list[str] | None = None) -> dict[str, Any]:
    base = panels or DEFAULT_PANELS
    cols = {"minimal": 1, "operator": 2, "engineering": 3, "immersive": 3, "cinematic": 4}.get(mode, 2)
    return {"mode": mode, "columns": cols, "panels": base, "draggable": True, "persistent": True}

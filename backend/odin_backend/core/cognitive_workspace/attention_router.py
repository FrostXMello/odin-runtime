from __future__ import annotations
from typing import Any


def route_attention(*, focus: str, panels: list[str]) -> dict[str, Any]:
    primary = panels[0] if panels else "chat"
    if "reasoning" in focus.lower():
        primary = "reasoning"
    elif "mission" in focus.lower():
        primary = "missions"
    return {"primary_panel": primary, "focus": focus[:120]}

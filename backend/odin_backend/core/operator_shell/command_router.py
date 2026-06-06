"""Command routing."""

from __future__ import annotations

from typing import Any


COMMANDS: dict[str, str] = {
    "show failed missions": "missions.failed",
    "resume yesterday's session": "session.resume",
    "optimize runtime for battery": "performance.battery",
    "show diagnostics": "diagnostics.snapshot",
}


def route_command(text: str) -> dict[str, Any]:
    key = text.strip().lower()
    if key in COMMANDS:
        return {"matched": True, "route": COMMANDS[key], "text": text}
    for pattern, route in COMMANDS.items():
        if pattern in key:
            return {"matched": True, "route": route, "text": text}
    return {"matched": False, "route": "search", "text": text}

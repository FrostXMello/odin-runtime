from __future__ import annotations

ACTIONS = ("assist", "debug", "mission", "voice", "focus")

def quick(action: str) -> dict:
    a = action if action in ACTIONS else "assist"
    return {"action": a, "supervised": True}

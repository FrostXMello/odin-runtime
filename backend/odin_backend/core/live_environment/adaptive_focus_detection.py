from __future__ import annotations

def focus(*, switches: int, duration_s: float) -> dict:
    focused = switches < 5 and duration_s > 300
    return {"focused": focused, "switches": switches, "state": "focus" if focused else "distraction"}

from __future__ import annotations

def handle_interrupt(*, speaking: bool) -> dict:
    return {"interrupted": speaking, "resume": not speaking}

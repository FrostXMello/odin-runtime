from __future__ import annotations

def dock(*, items: list[str] | None = None) -> dict:
    return {"items": items or ["cognition", "missions", "engineering", "voice"], "tray": True}

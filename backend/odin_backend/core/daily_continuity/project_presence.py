from __future__ import annotations

def presence(*, project: str, active: bool) -> dict:
    return {"project": project, "active": active}

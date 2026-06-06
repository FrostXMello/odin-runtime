from __future__ import annotations

def panels(*, count: int = 4) -> dict:
    return {"panels": min(count, 8), "unified": True}

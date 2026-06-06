from __future__ import annotations

def annotate(*, target: str, note: str) -> dict:
    return {"target": target, "note": note[:200]}

from __future__ import annotations

def validate(*, diff: str) -> dict:
    ok = "<<<<<<" not in diff and len(diff) < 500000
    return {"valid": ok, "reason": "ok" if ok else "conflict_markers_or_too_large"}

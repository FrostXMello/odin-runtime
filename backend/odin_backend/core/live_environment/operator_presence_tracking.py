from __future__ import annotations

def track(*, active: bool, duration_s: float) -> dict:
    return {"active": active, "duration_s": duration_s}

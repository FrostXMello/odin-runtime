from __future__ import annotations


def coordinate(*, horizon_days: int = 3) -> dict:
    return {"horizon_days": min(horizon_days, 14), "bounded": True}

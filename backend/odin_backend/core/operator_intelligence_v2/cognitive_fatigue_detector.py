from __future__ import annotations


def detect(*, hours: float) -> dict:
    fatigued = hours > 8
    return {"fatigued": fatigued, "hours": hours}

from __future__ import annotations

INTERVALS = {"survival": 120, "lightweight": 60, "balanced": 30, "immersive": 15, "overnight": 90, "cinematic": 10}


def schedule(profile: str) -> int:
    return INTERVALS.get(profile, 30)

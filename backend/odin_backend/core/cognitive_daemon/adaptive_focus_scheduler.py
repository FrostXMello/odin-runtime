from __future__ import annotations

PROFILES = {"ultra_light": 60, "balanced": 30, "immersive": 15, "cinematic": 10}


def tick_interval(profile: str) -> int:
    return PROFILES.get(profile, 30)

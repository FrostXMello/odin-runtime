from __future__ import annotations

INTENSITY = {"survival": 0.2, "balanced": 0.5, "immersive": 0.8, "cinematic": 0.9, "overnight_autonomous": 0.15}


def intensity(profile: str) -> float:
    return INTENSITY.get(profile, 0.5)

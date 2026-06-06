from __future__ import annotations

CAPS = {"survival": 8, "lightweight": 15, "balanced": 30, "immersive": 45, "overnight": 6, "cinematic": 60}


def balance(profile: str) -> dict:
    return {"fps_cap": CAPS.get(profile, 30), "agent_limit": 2 if profile in ("survival", "lightweight") else 4}

from __future__ import annotations

PROFILES = ("default", "engineering", "calm", "energetic")

def profile(name: str = "default") -> dict:
    p = name if name in PROFILES else "default"
    return {"profile": p, "wpm": 150 if p == "energetic" else 130}

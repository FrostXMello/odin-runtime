from __future__ import annotations
from typing import Any

IMMERSIVE = ("minimal", "operator", "engineering", "immersive", "cinematic")


def focus_profile(mode: str) -> dict[str, Any]:
    fps = {"minimal": 15, "operator": 24, "engineering": 30, "immersive": 45, "cinematic": 60}
    return {
        "mode": mode if mode in IMMERSIVE else "operator",
        "fps_cap": fps.get(mode, 30),
        "fullscreen_cognition": mode in ("immersive", "cinematic"),
        "split_reasoning": mode in ("engineering", "immersive", "cinematic"),
    }

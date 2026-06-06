"""Adaptive UI rendering state."""

from __future__ import annotations

from typing import Any

MODES = ("minimal", "balanced", "immersive", "cinematic")


def ui_state(*, mode: str, fps_target: int = 30) -> dict[str, Any]:
    m = mode if mode in MODES else "balanced"
    throttle = {"minimal": 15, "balanced": 30, "immersive": 45, "cinematic": 60}.get(m, 30)
    return {
        "mode": m,
        "fps_target": min(fps_target, throttle),
        "gpu_idle_release": m in ("minimal", "balanced"),
        "progressive_rendering": m in ("immersive", "cinematic"),
    }

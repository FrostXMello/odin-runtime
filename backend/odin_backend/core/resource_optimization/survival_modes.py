"""Resource survival modes for consumer hardware."""

from __future__ import annotations

from typing import Any

SURVIVAL_MODES = {
    "ultra_light": {"vram_cap_mb": 2048, "max_models": 1, "cognition_depth": 1, "batch_size": 1},
    "balanced": {"vram_cap_mb": 4096, "max_models": 2, "cognition_depth": 2, "batch_size": 2},
    "performance": {"vram_cap_mb": 6144, "max_models": 3, "cognition_depth": 3, "batch_size": 4},
    "overnight_daemon": {"vram_cap_mb": 2048, "max_models": 1, "cognition_depth": 1, "batch_size": 1, "idle_compact": True},
}


def survival_config(mode: str) -> dict[str, Any]:
    return dict(SURVIVAL_MODES.get(mode, SURVIVAL_MODES["balanced"]))

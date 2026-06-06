"""Safe startup recovery mode."""

from __future__ import annotations

from typing import Any


def safe_boot_plan() -> dict[str, Any]:
    return {
        "mode": "safe",
        "disable_background": True,
        "minimal_models": True,
        "skip_heavy_subsystems": ["world_simulation", "federation"],
    }

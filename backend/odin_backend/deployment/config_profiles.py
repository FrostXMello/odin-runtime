"""Hardware-aware config profiles."""

from __future__ import annotations

from typing import Any

PROFILES: dict[str, dict[str, Any]] = {
    "ultra_light": {"resource_mode": "minimal", "survival_mode": "ultra_light", "local_ai_warm_on_startup": False},
    "balanced": {"resource_mode": "normal", "survival_mode": "balanced", "local_ai_warm_on_startup": False},
    "performance": {"resource_mode": "normal", "survival_mode": "performance", "local_ai_warm_on_startup": True},
    "apple_silicon": {"resource_mode": "normal", "survival_mode": "balanced", "local_ai_warm_on_startup": True},
    "overnight": {"resource_mode": "lightweight", "survival_mode": "overnight_daemon", "daemon_mode_enabled": True},
}


def profile_config(name: str) -> dict[str, Any]:
    return dict(PROFILES.get(name, PROFILES["balanced"]))

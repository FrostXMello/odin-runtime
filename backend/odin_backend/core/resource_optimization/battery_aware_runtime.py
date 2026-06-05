"""Battery-aware throttling."""

from __future__ import annotations

from typing import Any


def throttle_factor(*, on_battery: bool, battery_pct: float) -> float:
    if not on_battery:
        return 1.0
    if battery_pct < 20:
        return 0.3
    if battery_pct < 50:
        return 0.6
    return 0.8

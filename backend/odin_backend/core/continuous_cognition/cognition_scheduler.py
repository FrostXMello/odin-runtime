from __future__ import annotations

from typing import Any


def should_tick(*, on_battery: bool, heavy_load: bool) -> bool:
    if heavy_load:
        return False
    if on_battery:
        return True
    return True

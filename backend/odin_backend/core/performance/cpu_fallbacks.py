"""CPU fallback routing."""

from __future__ import annotations


def use_cpu_fallback(*, vram_pressure: str, on_battery: bool) -> bool:
    return vram_pressure in ("high", "critical") or on_battery

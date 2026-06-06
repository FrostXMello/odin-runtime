"""Hardware detection for deployment profiles."""

from __future__ import annotations

import platform
from typing import Any


def detect_hardware(*, ram_mb: int = 16384, vram_mb: int = 4096) -> dict[str, Any]:
    system = platform.system().lower()
    profile = "balanced"
    if ram_mb <= 16384 and vram_mb <= 4096:
        profile = "ultra_light"
    elif ram_mb >= 32768:
        profile = "performance"
    if system == "darwin" and "arm" in platform.machine().lower():
        profile = "apple_silicon"
    return {
        "os": system,
        "machine": platform.machine(),
        "ram_mb": ram_mb,
        "vram_mb": vram_mb,
        "recommended_profile": profile,
    }

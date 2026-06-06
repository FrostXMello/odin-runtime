"""Self-optimizing model routing preferences."""
from __future__ import annotations
from typing import Any

MODES = ("lightweight", "balanced", "overnight_daemon")

def optimize_route(*, vram_mb: int = 4096, mode: str = "balanced") -> dict[str, Any]:
    m = mode if mode in MODES else "balanced"
    if vram_mb <= 4096:
        return {"route": "local_small", "mode": m, "vram_cap_mb": 3500, "latency_priority": True}
    return {"route": "local_balanced", "mode": m, "vram_cap_mb": vram_mb, "latency_priority": False}

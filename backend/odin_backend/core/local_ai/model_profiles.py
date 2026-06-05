"""Production model profiles for local inference."""

from __future__ import annotations

from typing import Any

PROFILES: dict[str, dict[str, Any]] = {
    "fast": {"name": "fast", "latency_target_ms": 200, "vram_mb": 512, "reasoning_depth": "low"},
    "reasoning": {"name": "reasoning", "latency_target_ms": 2000, "vram_mb": 2048, "reasoning_depth": "high"},
    "embedding": {"name": "embedding", "latency_target_ms": 100, "vram_mb": 256, "reasoning_depth": "none"},
    "code": {"name": "code", "latency_target_ms": 1500, "vram_mb": 1536, "reasoning_depth": "medium"},
}


def get_profile(role: str) -> dict[str, Any]:
    return dict(PROFILES.get(role, PROFILES["fast"]))

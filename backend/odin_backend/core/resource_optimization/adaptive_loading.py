"""Adaptive model loading by resource availability."""

from __future__ import annotations

from typing import Any


def should_load(*, vram_available_mb: int, model_size_mb: int, mode: str) -> bool:
    if mode == "lightweight":
        return model_size_mb <= 512
    return model_size_mb <= vram_available_mb

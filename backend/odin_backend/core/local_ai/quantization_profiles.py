"""Dynamic quantization selection by VRAM."""

from __future__ import annotations

from typing import Any


def select_quantization(*, vram_mb: int, model_size_mb: int) -> str:
    if vram_mb < 2048:
        return "q4_k_m"
    if vram_mb < 4096:
        return "q5_k_m"
    if model_size_mb > vram_mb * 0.7:
        return "q4_k_m"
    return "q8_0"


def profile_for_hardware(vram_mb: int = 4096, ram_mb: int = 16384) -> dict[str, Any]:
    return {
        "quantization": select_quantization(vram_mb=vram_mb, model_size_mb=3072),
        "max_context": 4096 if ram_mb < 16384 else 8192,
        "cpu_fallback": vram_mb < 1024,
    }

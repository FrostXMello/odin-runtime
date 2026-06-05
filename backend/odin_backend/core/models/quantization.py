"""Quantization level helpers for GGUF / local models."""

from __future__ import annotations

from enum import StrEnum


class QuantizationLevel(StrEnum):
    NONE = "none"
    Q4_K_M = "q4_k_m"
    Q5_K_M = "q5_k_m"
    Q8_0 = "q8_0"
    F16 = "f16"


_RAM_MULTIPLIER = {
    QuantizationLevel.NONE: 1.0,
    QuantizationLevel.F16: 0.9,
    QuantizationLevel.Q8_0: 0.55,
    QuantizationLevel.Q5_K_M: 0.4,
    QuantizationLevel.Q4_K_M: 0.32,
}


def estimate_ram_mb(base_mb: int, quant: str | QuantizationLevel) -> int:
    try:
        level = QuantizationLevel(quant)
    except ValueError:
        level = QuantizationLevel.Q4_K_M
    return int(base_mb * _RAM_MULTIPLIER.get(level, 0.5))

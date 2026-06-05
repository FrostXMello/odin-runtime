"""Voice activity detection stub."""

from __future__ import annotations


def is_speech_active(*, energy: float, threshold: float = 0.3) -> bool:
    return energy > threshold

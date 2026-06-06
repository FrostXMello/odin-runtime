from __future__ import annotations


def voice_attention(*, energy: float) -> str:
    if energy > 0.8:
        return "focused"
    if energy > 0.4:
        return "engaged"
    return "passive"

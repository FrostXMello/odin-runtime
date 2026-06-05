"""Voice latency optimization."""

from __future__ import annotations

from typing import Any


def optimize(*, stt_ms: float, llm_ms: float, tts_ms: float) -> dict[str, Any]:
    total = stt_ms + llm_ms + tts_ms
    return {"total_ms": total, "bottleneck": "llm" if llm_ms > stt_ms and llm_ms > tts_ms else "stt" if stt_ms > tts_ms else "tts"}

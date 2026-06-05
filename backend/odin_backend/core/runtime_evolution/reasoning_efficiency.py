"""Reasoning efficiency metrics."""

from __future__ import annotations

from typing import Any


def efficiency(*, tokens: int, success: bool, latency_ms: float) -> dict[str, Any]:
    score = (1.0 if success else 0.3) / max(tokens / 1000, 0.1) / max(latency_ms / 100, 0.1)
    return {"efficiency_score": round(min(score, 10.0), 4), "tokens": tokens, "latency_ms": latency_ms}

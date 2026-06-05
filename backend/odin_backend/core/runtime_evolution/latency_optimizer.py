"""Latency optimization recommendations."""

from __future__ import annotations

from typing import Any


def recommend(*, p50: float, p99: float) -> dict[str, Any]:
    return {"p50_ms": p50, "p99_ms": p99, "recommendation": "increase_cache" if p99 > p50 * 3 else "stable"}

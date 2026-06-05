"""Strategy learning from mission outcomes."""

from __future__ import annotations

from typing import Any


def update_strategy_stats(
    stats: dict[str, dict[str, float]],
    *,
    strategy_kind: str,
    success: bool,
    latency_ms: float | None = None,
) -> dict[str, dict[str, float]]:
    bucket = stats.setdefault(
        strategy_kind,
        {
            "attempts": 0.0,
            "successes": 0.0,
            "total_latency_ms": 0.0,
        },
    )
    bucket["attempts"] += 1
    if success:
        bucket["successes"] += 1
    if latency_ms:
        bucket["total_latency_ms"] += latency_ms
    return stats

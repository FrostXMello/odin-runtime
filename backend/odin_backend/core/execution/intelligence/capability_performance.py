"""Capability performance tracking."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


class CapabilityPerformanceTracker:
    def __init__(self) -> None:
        self._stats: dict[str, dict[str, float]] = defaultdict(
            lambda: {"attempts": 0, "successes": 0, "total_latency_ms": 0, "failures": 0}
        )

    def record(
        self,
        capability: str,
        *,
        success: bool,
        latency_ms: float | None = None,
    ) -> None:
        s = self._stats[capability]
        s["attempts"] += 1
        if success:
            s["successes"] += 1
        else:
            s["failures"] += 1
        if latency_ms:
            s["total_latency_ms"] += latency_ms

    def scores(self) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for cap, s in self._stats.items():
            attempts = s["attempts"] or 1
            out[cap] = {
                "attempts": s["attempts"],
                "success_rate": s["successes"] / attempts,
                "failure_rate": s["failures"] / attempts,
                "avg_latency_ms": s["total_latency_ms"] / attempts if attempts else 0,
                "reliability": s["successes"] / attempts,
                "throughput_score": min(1.0, attempts / 100.0),
            }
        return out

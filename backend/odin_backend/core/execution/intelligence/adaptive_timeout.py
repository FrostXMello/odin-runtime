"""Dynamic timeout estimation from history."""

from __future__ import annotations


def estimate_timeout(
    capability: str,
    *,
    base_seconds: float = 120.0,
    avg_latency_ms: float | None = None,
    failure_rate: float = 0.0,
) -> float:
    if avg_latency_ms:
        est = (avg_latency_ms / 1000.0) * 2.5
        est = max(base_seconds * 0.5, min(base_seconds * 3.0, est))
    else:
        est = base_seconds
    if failure_rate > 0.4:
        est *= 1.25
    return est

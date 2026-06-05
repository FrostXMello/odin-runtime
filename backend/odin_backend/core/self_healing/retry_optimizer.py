"""Retry path optimization."""

from __future__ import annotations


def optimize_retry(*, attempt: int, failure_rate: float, base_delay: float = 2.0) -> dict[str, float | str]:
    if failure_rate > 0.7:
        return {"delay_s": base_delay * (attempt + 1) * 2, "strategy": "backoff_aggressive"}
    if failure_rate > 0.4:
        return {"delay_s": base_delay * (attempt + 1), "strategy": "backoff_linear"}
    return {"delay_s": base_delay, "strategy": "immediate"}

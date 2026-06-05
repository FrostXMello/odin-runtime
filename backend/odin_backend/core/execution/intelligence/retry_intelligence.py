"""Adaptive retry strategies."""

from __future__ import annotations


def retry_delay(
    *,
    attempt: int,
    base_seconds: float = 2.0,
    failure_rate: float = 0.0,
    plan_confidence: float = 0.75,
) -> float:
    delay = base_seconds * (2 ** max(0, attempt - 1))
    if failure_rate > 0.5:
        delay *= 1.5
    if plan_confidence < 0.4:
        delay *= 0.75
    return min(120.0, delay)


def should_replan_instead_of_retry(
    *,
    attempt: int,
    max_retries: int,
    failure_rate: float,
    oscillation_score: float,
) -> bool:
    if oscillation_score >= 3:
        return True
    if attempt >= max_retries - 1 and failure_rate > 0.6:
        return True
    return False

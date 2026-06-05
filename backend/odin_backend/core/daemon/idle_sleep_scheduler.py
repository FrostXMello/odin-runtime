"""Idle sleep scheduling for daemon mode."""

from __future__ import annotations

from typing import Any


def sleep_interval(*, idle: bool, on_battery: bool) -> float:
    if idle and on_battery:
        return 30.0
    if idle:
        return 15.0
    return 5.0


def should_wake(*, activity_score: float, threshold: float = 0.3) -> bool:
    return activity_score >= threshold

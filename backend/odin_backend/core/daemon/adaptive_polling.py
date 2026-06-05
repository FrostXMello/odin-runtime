"""Adaptive polling intervals."""

from __future__ import annotations


def poll_interval(*, pressure: str, idle: bool) -> float:
    if pressure == "critical":
        return 60.0
    if idle:
        return 20.0
    if pressure == "high":
        return 10.0
    return 5.0

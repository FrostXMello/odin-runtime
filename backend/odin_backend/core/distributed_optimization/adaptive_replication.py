"""Adaptive memory replication."""

from __future__ import annotations

from typing import Any


def replication_factor(*, trust: float, load: float) -> int:
    if trust < 0.4 or load > 0.8:
        return 1
    return 2 if trust > 0.7 else 1

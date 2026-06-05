"""Adaptive compute allocation."""

from __future__ import annotations

from typing import Any


def allocate(*, available: float, demands: list[float]) -> list[float]:
    total = sum(demands) or 1.0
    return [round(available * d / total, 4) for d in demands]

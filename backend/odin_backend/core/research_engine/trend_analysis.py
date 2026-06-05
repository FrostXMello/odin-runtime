"""Detect trends from temporal knowledge."""

from __future__ import annotations

from typing import Any


def analyze_trends(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(history) < 2:
        return []
    first = history[0].get("confidence", 0.5)
    last = history[-1].get("confidence", 0.5)
    delta = last - first
    direction = "rising" if delta > 0.05 else "falling" if delta < -0.05 else "stable"
    return [{"direction": direction, "delta": delta, "samples": len(history)}]

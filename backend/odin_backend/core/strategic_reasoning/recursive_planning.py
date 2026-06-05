"""Recursive multi-step planning."""

from __future__ import annotations

from typing import Any


def recursive_plan(goal: str, *, depth: int = 3) -> list[dict[str, Any]]:
    depth = min(depth, 8)
    return [
        {"level": i, "step": f"decompose_{goal}_L{i}", "confidence": round(0.9 - i * 0.1, 2)}
        for i in range(depth)
    ]

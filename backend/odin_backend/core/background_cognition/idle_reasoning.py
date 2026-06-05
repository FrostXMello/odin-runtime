"""Low-priority idle reasoning cycles."""

from __future__ import annotations

from typing import Any


def idle_reason(*, topic: str, depth: int = 1) -> dict[str, Any]:
    depth = min(depth, 3)
    return {"topic": topic, "depth": depth, "priority": "low", "confidence": 0.55}

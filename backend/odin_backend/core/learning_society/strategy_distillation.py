"""Distill successful strategies."""

from __future__ import annotations

from typing import Any


def distill(strategy: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": strategy.get("name", "unnamed"),
        "steps": strategy.get("steps", [])[:8],
        "confidence": strategy.get("confidence", 0.5),
    }

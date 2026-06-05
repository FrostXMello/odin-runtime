"""Adaptive assistance without manipulation."""

from __future__ import annotations

from typing import Any


def suggest_assistance(*, style: str, context: str) -> dict[str, Any]:
    depth = {"hands_on": "detailed", "balanced": "medium", "autonomous_supervised": "brief"}.get(style, "medium")
    return {
        "suggestion": f"assist_with_{context}",
        "explanation_depth": depth,
        "transparent": True,
        "manipulative": False,
    }

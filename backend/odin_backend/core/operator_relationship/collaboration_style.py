"""Collaboration style adaptation."""

from __future__ import annotations

from typing import Any

STYLES = ("hands_on", "balanced", "autonomous_supervised")


def adapt_style(interaction_count: int) -> str:
    if interaction_count < 5:
        return "hands_on"
    if interaction_count < 20:
        return "balanced"
    return "autonomous_supervised"

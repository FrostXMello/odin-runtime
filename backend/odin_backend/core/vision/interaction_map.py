"""Interaction map — read-only UI regions (no autonomous clicking)."""

from __future__ import annotations

from typing import Any


def build_interaction_map(ui_elements: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "regions": ui_elements,
        "automation_allowed": False,
        "read_only": True,
    }

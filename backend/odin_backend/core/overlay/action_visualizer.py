"""Visualize action targets."""

from __future__ import annotations

from typing import Any


def visualize_action(action: dict[str, Any]) -> dict[str, Any]:
    payload = action.get("payload", {})
    return {
        "kind": action.get("kind"),
        "label": action.get("label"),
        "target": {"x": payload.get("x"), "y": payload.get("y")},
        "highlight": True,
    }

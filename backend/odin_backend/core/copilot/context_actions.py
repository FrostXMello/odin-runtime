"""Contextual action recommendations (suggest only)."""

from __future__ import annotations

from typing import Any


def contextual_actions(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    actions: list[dict] = []
    if snapshot.get("has_code"):
        actions.append({"action": "suggest_test_run", "label": "Run tests"})
    if snapshot.get("app_hint") == "terminal":
        actions.append({"action": "suggest_command_review", "label": "Review last command"})
    actions.append({"action": "capture_snapshot", "label": "Capture screen context"})
    return actions

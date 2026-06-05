"""Predict next workflow steps from workspace patterns."""

from __future__ import annotations

from typing import Any


def predict_next(patterns: list[dict[str, Any]]) -> list[str]:
    if not patterns:
        return ["Review active task", "Capture workspace snapshot"]
    last = patterns[-1]
    apps = last.get("apps", []) or [last.get("label", "")]
    if "code" in str(apps).lower():
        return ["Run linter", "Commit changes", "Record workflow macro"]
    return ["Summarize session", "Archive notes", "Replay last macro"]

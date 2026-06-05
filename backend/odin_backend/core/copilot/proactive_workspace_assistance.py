"""Proactive workspace assistance."""

from __future__ import annotations

from typing import Any


def suggest(*, focus_app: str, patterns: list[str]) -> list[dict[str, Any]]:
    out = []
    if focus_app and "terminal" in focus_app.lower():
        out.append({"suggestion": "run_tests", "confidence": 0.65})
    if "commit" in " ".join(patterns).lower():
        out.append({"suggestion": "review_diff", "confidence": 0.7})
    return out

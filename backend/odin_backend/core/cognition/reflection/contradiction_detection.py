"""Detect contradictions in plans and reasoning."""

from __future__ import annotations

from typing import Any


def detect_contradictions(text: str) -> list[dict[str, Any]]:
    lower = text.lower()
    issues: list[dict[str, Any]] = []
    pairs = [
        ("parallel", "sequential"),
        ("skip validation", "validate"),
        ("no retry", "retry"),
        ("unsafe", "safe execution"),
    ]
    for a, b in pairs:
        if a in lower and b in lower:
            issues.append({"kind": "contradiction", "terms": [a, b]})
    if "always" in lower and "never" in lower:
        issues.append({"kind": "contradiction", "terms": ["always", "never"]})
    return issues

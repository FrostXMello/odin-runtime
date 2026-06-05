"""Detected workflow patterns per project."""

from __future__ import annotations

from collections import Counter
from typing import Any


def detect_patterns(events: list[dict[str, Any]]) -> list[str]:
    kinds = Counter(e.get("kind", "unknown") for e in events)
    return [f"{k}:{v}" for k, v in kinds.most_common(5)]

from __future__ import annotations

from typing import Any


def detect_regression(*, before: str, after: str) -> dict[str, Any]:
    removed = sum(1 for w in before.split() if w not in after.split())
    return {"regression": removed > len(before.split()) * 0.5, "removed_signals": removed}

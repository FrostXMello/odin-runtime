"""Recursive task decomposition."""

from __future__ import annotations

from typing import Any


def decompose(title: str, *, depth: int = 3) -> list[dict[str, Any]]:
    depth = min(depth, 5)
    return [{"level": i, "subtask": f"{title}_sub_{i}"} for i in range(depth)]

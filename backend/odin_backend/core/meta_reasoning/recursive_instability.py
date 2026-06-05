"""Recursive loop instability detection."""

from __future__ import annotations

from typing import Any


def detect(depth: int, *, max_depth: int = 8) -> dict[str, Any]:
    return {"unstable": depth > max_depth, "depth": depth, "max_depth": max_depth}

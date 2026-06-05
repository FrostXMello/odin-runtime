"""Reasoning diagnostics."""

from __future__ import annotations

from typing import Any


def diagnose(*, loop_depth: int, contradiction_count: int) -> dict[str, Any]:
    unstable = loop_depth > 5 or contradiction_count > 3
    return {"unstable": unstable, "loop_depth": loop_depth, "contradictions": contradiction_count}

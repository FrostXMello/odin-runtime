"""Optimize repeated workflow patterns."""

from __future__ import annotations

from typing import Any


def optimize_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(steps) < 2:
        return steps
    deduped: list[dict] = []
    prev_key = None
    for step in steps:
        key = (step.get("kind"), str(step.get("payload")))
        if key != prev_key:
            deduped.append(step)
        prev_key = key
    return deduped

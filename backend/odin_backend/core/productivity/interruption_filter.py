"""Interruption filtering during focus."""

from __future__ import annotations


def should_interrupt(*, focus_active: bool, priority: str) -> bool:
    if not focus_active:
        return True
    return priority in ("urgent", "critical")

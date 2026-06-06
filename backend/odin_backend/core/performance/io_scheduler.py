"""I/O scheduling priorities."""

from __future__ import annotations


def io_priority(*, background: bool) -> str:
    return "low" if background else "normal"

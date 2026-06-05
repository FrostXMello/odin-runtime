"""Filesystem change detection."""

from __future__ import annotations

from typing import Any


def detect_changes(*, before: set[str], after: set[str]) -> dict[str, Any]:
    added = after - before
    removed = before - after
    return {"added": list(added)[:20], "removed": list(removed)[:20], "changed_count": len(added) + len(removed)}

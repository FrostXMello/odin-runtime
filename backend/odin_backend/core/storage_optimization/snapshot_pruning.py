"""Snapshot pruning."""

from __future__ import annotations

from typing import Any


def prune_snapshots(snapshots: list[dict[str, Any]], *, max_count: int = 30) -> list[dict[str, Any]]:
    return snapshots[-max_count:]

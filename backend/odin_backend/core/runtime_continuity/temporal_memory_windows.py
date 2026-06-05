"""Temporal memory window management."""

from __future__ import annotations

from typing import Any


class TemporalMemoryWindows:
    def __init__(self) -> None:
        self._windows: dict[str, list[dict[str, Any]]] = {}

    def open(self, window_id: str, *, start: str, end: str) -> dict[str, Any]:
        self._windows.setdefault(window_id, []).append({"start": start, "end": end, "entries": []})
        return {"window_id": window_id, "status": "open"}

    def append(self, window_id: str, entry: dict) -> None:
        if window_id in self._windows and self._windows[window_id]:
            self._windows[window_id][-1].setdefault("entries", []).append(entry)

    def snapshot(self) -> dict[str, Any]:
        return {"window_count": len(self._windows), "windows": {k: len(v) for k, v in self._windows.items()}}

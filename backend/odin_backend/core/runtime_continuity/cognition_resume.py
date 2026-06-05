"""Resume interrupted cognition."""

from __future__ import annotations

from typing import Any


class CognitionResume:
    def __init__(self) -> None:
        self._deferred: list[dict[str, Any]] = []

    def defer(self, *, kind: str, payload: dict) -> dict[str, Any]:
        entry = {"kind": kind, "payload": payload, "status": "deferred"}
        self._deferred.append(entry)
        return entry

    def pending(self) -> list[dict[str, Any]]:
        return [d for d in self._deferred if d["status"] == "deferred"]

    def resume_all(self) -> list[dict[str, Any]]:
        resumed = []
        for d in self._deferred:
            if d["status"] == "deferred":
                d["status"] = "resumed"
                resumed.append(d)
        return resumed

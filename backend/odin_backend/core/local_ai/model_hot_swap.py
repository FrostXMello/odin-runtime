"""Hot-swappable active reasoning model."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ModelHotSwap:
    def __init__(self) -> None:
        self._active: str | None = None
        self._history: list[dict[str, Any]] = []

    def swap(self, model_name: str) -> dict[str, Any]:
        prev = self._active
        self._active = model_name
        entry = {"from": prev, "to": model_name, "at": datetime.now(timezone.utc).isoformat()}
        self._history.append(entry)
        return entry

    @property
    def active(self) -> str | None:
        return self._active

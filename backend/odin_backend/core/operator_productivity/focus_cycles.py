from __future__ import annotations
from typing import Any


class FocusCycles:
    def __init__(self) -> None:
        self._cycle_min = 25

    def start(self, *, minutes: int = 25) -> dict[str, Any]:
        self._cycle_min = minutes
        return {"minutes": minutes, "started": True}

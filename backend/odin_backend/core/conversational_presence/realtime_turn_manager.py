from __future__ import annotations
from typing import Any


class RealtimeTurnManager:
    def __init__(self) -> None:
        self._turn = 0

    def next_turn(self) -> int:
        self._turn += 1
        return self._turn

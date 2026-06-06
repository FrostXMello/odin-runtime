from __future__ import annotations
from typing import Any


class LiveChainTracker:
    def __init__(self) -> None:
        self._chains: list[dict] = []

    def push(self, step: str, *, confidence: float = 0.7) -> dict[str, Any]:
        node = {"step": step, "confidence": confidence}
        self._chains.append(node)
        return node

    def snapshot(self) -> list[dict]:
        return self._chains[-24:]

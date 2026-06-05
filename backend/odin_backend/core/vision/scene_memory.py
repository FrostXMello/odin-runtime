"""Scene memory for visual reasoning chains."""

from __future__ import annotations

from collections import deque
from typing import Any


class SceneMemory:
    def __init__(self, *, max_scenes: int = 24) -> None:
        self._scenes: deque[dict[str, Any]] = deque(maxlen=max_scenes)

    def add(self, scene: dict[str, Any]) -> None:
        self._scenes.append(scene)

    def recent(self, *, limit: int = 8) -> list[dict[str, Any]]:
        return list(self._scenes)[-limit:]

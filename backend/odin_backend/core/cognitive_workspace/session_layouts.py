from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_workspace.workspace_state import load_layout, save_layout


class SessionLayouts:
    def __init__(self, path: str = "./data/cognitive_workspace_layout.json") -> None:
        self._path = path

    def persist(self, layout: dict) -> dict[str, Any]:
        return save_layout(path=self._path, layout=layout)

    def restore(self) -> dict[str, Any]:
        return load_layout(path=self._path)

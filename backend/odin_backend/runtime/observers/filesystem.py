"""Filesystem observer — lightweight change detection."""

from pathlib import Path
from typing import Any

from odin_backend.models.perception import PerceptionCategory, PerceptionRecord
from odin_backend.runtime.observers.base import BaseRuntimeObserver


class FilesystemObserver(BaseRuntimeObserver):
    name = "filesystem"
    interval_seconds = 30.0

    def __init__(self, perception_engine: Any, watch_path: str = "./data") -> None:
        super().__init__(perception_engine)
        self._path = Path(watch_path)
        self._mtime: float | None = None

    async def poll(self) -> list[PerceptionRecord]:
        if not self._path.exists():
            return []
        try:
            mtime = self._path.stat().st_mtime
        except OSError:
            return []
        if self._mtime is not None and mtime == self._mtime:
            return []
        self._mtime = mtime
        return [
            PerceptionRecord(
                category=PerceptionCategory.ENVIRONMENT_CHANGE,
                source=self.name,
                summary=f"Filesystem activity under {self._path}",
                payload={"path": str(self._path), "mtime": mtime},
            )
        ]

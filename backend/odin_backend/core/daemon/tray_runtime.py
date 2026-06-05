"""System tray runtime stub."""

from __future__ import annotations

from typing import Any


class TrayRuntime:
    def __init__(self) -> None:
        self._visible = False

    def show(self) -> dict[str, str]:
        self._visible = True
        return {"status": "tray_visible"}

    def hide(self) -> dict[str, str]:
        self._visible = False
        return {"status": "tray_hidden"}

"""Action execution context."""

from __future__ import annotations

from typing import Any


class ActionContext:
    def __init__(self) -> None:
        self._vars: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._vars[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._vars.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        return dict(self._vars)

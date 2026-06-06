"""Secure credential vault (local)."""

from __future__ import annotations

from typing import Any


class SecureCredentials:
    def __init__(self) -> None:
        self._vault: dict[str, str] = {}

    def store(self, key: str, value: str) -> None:
        self._vault[key] = value

    def get(self, key: str) -> str | None:
        return self._vault.get(key)

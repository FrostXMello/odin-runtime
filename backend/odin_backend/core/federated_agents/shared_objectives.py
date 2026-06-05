"""Federated objective assignment."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class SharedObjectives:
    def __init__(self) -> None:
        self._objectives: list[dict[str, Any]] = []

    def assign(self, *, owner_node: str, title: str, shared_with: list[str]) -> dict[str, Any]:
        obj = {
            "id": str(uuid4()),
            "owner_node": owner_node,
            "title": title,
            "shared_with": shared_with,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._objectives.append(obj)
        return obj

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._objectives)

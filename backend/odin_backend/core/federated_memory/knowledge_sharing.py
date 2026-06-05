"""Distilled knowledge sharing."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class KnowledgeSharing:
    def __init__(self) -> None:
        self._shares: list[dict[str, Any]] = []

    def share(self, *, from_node: str, fact: str, confidence: float, lineage: str) -> dict[str, Any]:
        entry = {
            "id": str(uuid4()),
            "from_node": from_node,
            "fact": fact,
            "confidence": confidence,
            "lineage": lineage,
            "shared_at": datetime.now(timezone.utc).isoformat(),
        }
        self._shares.append(entry)
        return entry

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._shares)

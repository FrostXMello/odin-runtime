"""Cross-node dialogue sessions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class FederationDialogue:
    def __init__(self) -> None:
        self._sessions: list[dict[str, Any]] = []

    def start(self, *, topic: str, node_ids: list[str]) -> dict[str, Any]:
        session = {
            "id": str(uuid4()),
            "topic": topic,
            "participants": node_ids,
            "status": "active",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        self._sessions.append(session)
        return session

    def list_active(self) -> list[dict[str, Any]]:
        return [s for s in self._sessions if s["status"] == "active"]

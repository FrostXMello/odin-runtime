"""Long-horizon objective chains for strategic reasoning."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class LongHorizonObjectives:
    def __init__(self) -> None:
        self._chains: list[dict[str, Any]] = []

    def create(self, *, title: str, horizon_days: int = 30) -> dict[str, Any]:
        chain = {
            "id": str(uuid4()),
            "title": title,
            "horizon_days": min(horizon_days, 365),
            "milestones": [],
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._chains.append(chain)
        return chain

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._chains)

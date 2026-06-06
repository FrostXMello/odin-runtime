from __future__ import annotations
from typing import Any
from uuid import uuid4

class AutonomousBacklog:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def add(self, *, title: str, impact: str, confidence: float, cost: str = "medium") -> dict[str, Any]:
        item = {
            "id": str(uuid4()),
            "title": title[:200],
            "impact": impact,
            "confidence": round(confidence, 3),
            "cost": cost,
            "status": "proposed",
            "approval_required": True,
        }
        self._items.append(item)
        self._items.sort(key=lambda x: (-x["confidence"], x["cost"] != "high"))
        return item

    def snapshot(self) -> list[dict]:
        return list(self._items)

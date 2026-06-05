"""Mission outcome prediction."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class PredictionEngine:
    def __init__(self) -> None:
        self._predictions: list[dict[str, Any]] = []

    def predict(self, *, mission_id: str | None, entity: str, hypothesis: str, confidence: float = 0.6) -> dict[str, Any]:
        pred = {
            "id": str(uuid4()),
            "mission_id": mission_id,
            "entity": entity,
            "hypothesis": hypothesis,
            "confidence": min(1.0, max(0.0, confidence)),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._predictions.append(pred)
        return pred

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._predictions)

    def list_for_mission(self, mission_id: str) -> list[dict[str, Any]]:
        return [p for p in self._predictions if p.get("mission_id") == mission_id]

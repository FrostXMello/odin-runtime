"""Long-term capability trend tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class CapabilityTracking:
    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def record(self, *, capability: str, score: float) -> dict[str, Any]:
        entry = {"capability": capability, "score": score, "at": datetime.now(timezone.utc).isoformat()}
        self._history.append(entry)
        return entry

    def trend(self, capability: str) -> dict[str, Any]:
        scores = [h["score"] for h in self._history if h["capability"] == capability]
        if len(scores) < 2:
            return {"trend": "stable", "scores": scores}
        return {"trend": "improving" if scores[-1] > scores[0] else "declining", "scores": scores[-5:]}

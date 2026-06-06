"""Track reasoning chain quality over time."""

from __future__ import annotations

from typing import Any


class ChainQualityTracker:
    def __init__(self) -> None:
        self._scores: list[float] = []

    def record(self, score: float) -> None:
        self._scores.append(max(0.0, min(1.0, score)))
        if len(self._scores) > 200:
            self._scores = self._scores[-200:]

    def snapshot(self) -> dict[str, Any]:
        if not self._scores:
            return {"count": 0, "avg": 0.0, "trend": "unknown"}
        avg = sum(self._scores) / len(self._scores)
        recent = sum(self._scores[-10:]) / min(10, len(self._scores))
        trend = "improving" if recent > avg else "stable" if abs(recent - avg) < 0.05 else "declining"
        return {"count": len(self._scores), "avg": round(avg, 3), "recent": round(recent, 3), "trend": trend}

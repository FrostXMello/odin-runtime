"""Per-agent expertise memory."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


class ExpertiseMemory:
    def __init__(self, *, max_per_agent: int = 40) -> None:
        self._records: dict[str, deque[dict[str, Any]]] = {}

    def record(self, agent_id: str, *, domain: str, score: float, source: str = "mission") -> None:
        q = self._records.setdefault(agent_id, deque(maxlen=self._max if hasattr(self, "_max") else 40))
        q.append(
            {
                "domain": domain,
                "score": score,
                "source": source,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def list_for(self, agent_id: str) -> list[dict[str, Any]]:
        return list(self._records.get(agent_id, []))

    def heatmap(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        counts: dict[str, int] = {}
        for records in self._records.values():
            for r in records:
                d = r["domain"]
                totals[d] = totals.get(d, 0.0) + r["score"]
                counts[d] = counts.get(d, 0) + 1
        return {d: round(totals[d] / counts[d], 3) for d in totals}

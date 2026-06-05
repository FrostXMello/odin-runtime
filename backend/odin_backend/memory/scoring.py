"""Memory importance scoring."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MemoryScore(BaseModel):
    memory_id: str
    score: float
    recency: float = 0.0
    frequency: float = 0.0
    project_relevance: float = 0.0
    retrieval_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryScorer:
    def __init__(self) -> None:
        self._access_counts: dict[str, int] = {}
        self._last_access: dict[str, datetime] = {}

    def record_access(self, memory_id: str) -> None:
        self._access_counts[memory_id] = self._access_counts.get(memory_id, 0) + 1
        self._last_access[memory_id] = datetime.now(timezone.utc)

    def score(
        self,
        memory_id: str,
        *,
        created_at: datetime | None = None,
        project: str | None = None,
        active_project: str | None = None,
    ) -> MemoryScore:
        now = datetime.now(timezone.utc)
        recency = 1.0
        if created_at:
            age_hours = (now - created_at).total_seconds() / 3600
            recency = max(0.1, 1.0 / (1.0 + age_hours / 24))

        frequency = min(1.0, self._access_counts.get(memory_id, 0) / 10)
        project_rel = 1.0 if project and active_project and project == active_project else 0.3

        total = recency * 0.4 + frequency * 0.35 + project_rel * 0.25
        return MemoryScore(
            memory_id=memory_id,
            score=round(total, 4),
            recency=recency,
            frequency=frequency,
            project_relevance=project_rel,
            retrieval_count=self._access_counts.get(memory_id, 0),
        )

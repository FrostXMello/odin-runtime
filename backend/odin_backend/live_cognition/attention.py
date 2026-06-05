"""Cognitive attention — prioritize operational signals."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AttentionPriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class AttentionItem(BaseModel):
    id: str
    message: str
    priority: AttentionPriority
    source: str
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float = 0.5


class CognitiveAttentionSystem:
    WEIGHTS = {
        AttentionPriority.CRITICAL: 1.0,
        AttentionPriority.HIGH: 0.75,
        AttentionPriority.NORMAL: 0.5,
        AttentionPriority.LOW: 0.25,
    }

    def __init__(self) -> None:
        self._items: list[AttentionItem] = []

    def prioritize(
        self,
        message: str,
        source: str,
        *,
        priority: AttentionPriority = AttentionPriority.NORMAL,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AttentionItem:
        import uuid

        item = AttentionItem(
            id=str(uuid.uuid4()),
            message=message,
            priority=priority,
            source=source,
            reason=reason or f"Attention from {source}",
            metadata=metadata or {},
            score=self.WEIGHTS[priority],
        )
        self._items.append(item)
        self._items.sort(key=lambda x: x.score, reverse=True)
        self._items = self._items[:100]
        return item

    def get_current_attention(self, limit: int = 10) -> list[AttentionItem]:
        return self._items[:limit]

    def on_workflow_failure(self, workflow_id: str, error: str) -> AttentionItem:
        return self.prioritize(
            f"Workflow {workflow_id} failed: {error[:120]}",
            "workflow",
            priority=AttentionPriority.CRITICAL,
            reason="Active workflow failure requires attention",
            metadata={"workflow_id": workflow_id},
        )

    def on_context_shift(self, insight: str) -> AttentionItem:
        return self.prioritize(
            insight,
            "context",
            priority=AttentionPriority.HIGH,
            reason="User focus or environment shift detected",
        )

    def on_security_anomaly(self, detail: str) -> AttentionItem:
        return self.prioritize(
            detail,
            "security",
            priority=AttentionPriority.CRITICAL,
            reason="Security policy or trust anomaly",
        )

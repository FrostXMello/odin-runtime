"""Cognitive priority engine — strict ranked focus."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.bus.signals import Signal, SignalKind
from odin_backend.core.context_graph.graph import GlobalContextGraph


class PriorityItemKind(StrEnum):
    TASK = "task"
    ALERT = "alert"
    RECOMMENDATION = "recommendation"
    MEMORY_RECALL = "memory_recall"
    WORKFLOW_ACTION = "workflow_action"


class PriorityItem(BaseModel):
    id: str
    kind: PriorityItemKind
    title: str
    score: float
    source: str
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CognitivePriorityEngine:
    """If everything is important, nothing is — enforce strict ranking."""

    MAX_VISIBLE = 10

    def __init__(self, graph: GlobalContextGraph) -> None:
        self._graph = graph
        self._items: list[PriorityItem] = []

    def ingest_signal(self, signal: Signal) -> None:
        item = self._signal_to_item(signal)
        if item:
            self._items.append(item)
            self._rebalance()

    def _signal_to_item(self, signal: Signal) -> PriorityItem | None:
        if signal.kind == SignalKind.WORKFLOW and signal.name.endswith("failed"):
            return PriorityItem(
                id=f"wf-{signal.workflow_id}",
                kind=PriorityItemKind.ALERT,
                title=f"Workflow failed: {signal.workflow_id or 'unknown'}",
                score=0.98,
                source="workflow",
                reason="Active workflow failure",
                metadata=signal.payload,
            )
        if signal.kind == SignalKind.SECURITY:
            return PriorityItem(
                id=f"sec-{signal.id}",
                kind=PriorityItemKind.ALERT,
                title=signal.name,
                score=0.97,
                source="security",
                reason="Security or policy signal",
                metadata=signal.payload,
            )
        if signal.kind == SignalKind.RECOMMENDATION:
            return PriorityItem(
                id=f"rec-{signal.id}",
                kind=PriorityItemKind.RECOMMENDATION,
                title=signal.payload.get("title", "Recommendation"),
                score=float(signal.payload.get("relevance", 0.6)),
                source="proactive",
                reason="Proactive assistance (requires approval)",
                metadata=signal.payload,
            )
        if signal.kind == SignalKind.MEMORY and "retrieved" in signal.name:
            return PriorityItem(
                id=f"mem-{signal.id}",
                kind=PriorityItemKind.MEMORY_RECALL,
                title="Relevant memory retrieved",
                score=0.55,
                source="memory",
                reason="Contextual memory relevance",
                metadata=signal.payload,
            )
        if signal.kind == SignalKind.WORKFLOW and "step" in signal.name:
            return PriorityItem(
                id=f"step-{signal.workflow_id}-{signal.id}",
                kind=PriorityItemKind.WORKFLOW_ACTION,
                title=f"Workflow step: {signal.name}",
                score=signal.priority_hint,
                source="workflow",
                reason="Active workflow progress",
                metadata=signal.payload,
            )
        if signal.kind == SignalKind.DESKTOP:
            return PriorityItem(
                id=f"ctx-{signal.id}",
                kind=PriorityItemKind.TASK,
                title="Desktop context shift",
                score=0.65,
                source="desktop",
                reason="Environmental awareness update",
                metadata=signal.payload,
            )
        return None

    def _rebalance(self) -> None:
        self._items.sort(key=lambda x: x.score, reverse=True)
        # Decay older duplicates
        seen: set[str] = set()
        unique: list[PriorityItem] = []
        for item in self._items:
            key = f"{item.kind}:{item.title[:40]}"
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        self._items = unique[: self.MAX_VISIBLE * 2]

    def rank(self, limit: int | None = None) -> list[PriorityItem]:
        cap = min(limit or self.MAX_VISIBLE, self.MAX_VISIBLE)
        return self._items[:cap]

    def top_focus(self) -> str:
        ranked = self.rank(1)
        if not ranked:
            return "Awaiting signals — system idle"
        return ranked[0].title

    def prune_to(self, limit: int) -> int:
        """Keep top N by score — used by stability loop."""
        before = len(self._items)
        self._items = self.rank(limit)
        return before - len(self._items)

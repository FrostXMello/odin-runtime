"""Reasoning graph for planner decisions."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ReasoningKind(StrEnum):
    ASSUMPTION = "assumption"
    INFERENCE = "inference"
    DEPENDENCY = "dependency"
    TOOL_DECISION = "tool_decision"
    VALIDATION = "validation"
    CONFIDENCE = "confidence"
    STRATEGY = "strategy"
    REPLAN = "replan"


class ReasoningNode(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid4()))
    kind: ReasoningKind
    message: str
    confidence: float = 0.75
    task_id: str | None = None
    parent_id: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_trace_payload(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind.value,
            "message": self.message,
            "confidence": self.confidence,
            "task_id": self.task_id,
            "parent_id": self.parent_id,
            "assumptions": self.assumptions,
            "evidence": self.evidence,
        }


class ReasoningGraph(BaseModel):
    nodes: list[ReasoningNode] = Field(default_factory=list)

    def add(
        self,
        kind: ReasoningKind,
        message: str,
        *,
        confidence: float = 0.75,
        task_id: str | None = None,
        parent_id: str | None = None,
        assumptions: list[str] | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> ReasoningNode:
        node = ReasoningNode(
            kind=kind,
            message=message,
            confidence=confidence,
            task_id=task_id,
            parent_id=parent_id,
            assumptions=assumptions or [],
            evidence=evidence or {},
        )
        self.nodes.append(node)
        return node

    def edges(self) -> list[dict[str, str]]:
        return [
            {"source": n.parent_id, "target": n.node_id, "kind": n.kind.value}
            for n in self.nodes
            if n.parent_id
        ]

    def snapshot(self) -> dict[str, Any]:
        return {
            "node_count": len(self.nodes),
            "nodes": [n.to_trace_payload() for n in self.nodes],
            "edges": self.edges(),
        }

"""Signal lineage graph for visualization export."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class SignalGraphNode(BaseModel):
    id: str
    kind: str  # signal | mission | task | policy | suppression
    label: str
    timestamp: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SignalGraphEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    target: str
    relation: str  # propagates_to | suppressed | policy_block | replay_block
    timestamp: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SignalGraphExport(BaseModel):
    generated_at: str
    node_count: int
    edge_count: int
    nodes: list[SignalGraphNode]
    edges: list[SignalGraphEdge]


class SignalLineageTracker:
    def __init__(self, *, max_records: int = 20_000) -> None:
        self._nodes: dict[str, SignalGraphNode] = {}
        self._edges: deque[SignalGraphEdge] = deque(maxlen=max_records)
        self._propagation_latency_ms: list[float] = []

    def record_signal(
        self,
        *,
        signal_id: str,
        signal_type: str,
        source: str,
        destination: str,
        path: list[str] | None = None,
        suppressed: bool = False,
        replay_blocked: bool = False,
        policy_interference: bool = False,
        latency_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        sid = f"signal:{signal_id}"
        self._nodes[sid] = SignalGraphNode(
            id=sid,
            kind="signal",
            label=signal_type,
            timestamp=now,
            metadata={"source": source, **(metadata or {})},
        )
        dest_id = f"dest:{destination}"
        if dest_id not in self._nodes:
            self._nodes[dest_id] = SignalGraphNode(
                id=dest_id,
                kind="destination",
                label=destination,
                timestamp=now,
            )
        relation = "propagates_to"
        if suppressed:
            relation = "suppressed"
        elif replay_blocked:
            relation = "replay_block"
        elif policy_interference:
            relation = "policy_block"
        self._edges.append(
            SignalGraphEdge(
                source=sid,
                target=dest_id,
                relation=relation,
                timestamp=now,
                metadata={"path": path or [], "source": source},
            )
        )
        if latency_ms is not None:
            self._propagation_latency_ms.append(latency_ms)
            if len(self._propagation_latency_ms) > 2000:
                self._propagation_latency_ms = self._propagation_latency_ms[-1000:]

    def link_mission_signal(self, mission_id: str, signal_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        mid = f"mission:{mission_id}"
        sid = f"signal:{signal_id}"
        if mid not in self._nodes:
            self._nodes[mid] = SignalGraphNode(id=mid, kind="mission", label=mission_id, timestamp=now)
        if sid in self._nodes:
            self._edges.append(
                SignalGraphEdge(source=sid, target=mid, relation="triggers", timestamp=now)
            )

    def export_graph(self, *, limit_edges: int = 500) -> SignalGraphExport:
        edges = list(self._edges)[-limit_edges:]
        node_ids = {e.source for e in edges} | {e.target for e in edges}
        nodes = [self._nodes[nid] for nid in node_ids if nid in self._nodes]
        return SignalGraphExport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            node_count=len(nodes),
            edge_count=len(edges),
            nodes=nodes,
            edges=edges,
        )

    def avg_propagation_latency_ms(self) -> float:
        if not self._propagation_latency_ms:
            return 0.0
        return sum(self._propagation_latency_ms) / len(self._propagation_latency_ms)

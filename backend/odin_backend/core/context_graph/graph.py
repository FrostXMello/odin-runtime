"""Global context graph — single system-wide truth."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.core.bus.signals import Signal, SignalKind
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class GraphNode(BaseModel):
    id: str
    node_type: str
    label: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str


class GlobalContextGraph:
    """Unified graph: users, projects, workflows, agents, tools, sessions, desktop."""

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []
        self._seed_system()

    def _seed_system(self) -> None:
        self.upsert_node("user:default", "user", "Operator", {"role": "owner"})
        self.upsert_node("project:PROJECT_ODIN", "project", "PROJECT_ODIN", {})
        self.upsert_node("system:odin", "system", "ODIN Kernel", {"version": "kernel"})

    def upsert_node(self, node_id: str, node_type: str, label: str, metadata: dict | None = None) -> GraphNode:
        node = GraphNode(
            id=node_id,
            node_type=node_type,
            label=label,
            metadata=metadata or {},
        )
        self._nodes[node_id] = node
        return node

    def link(self, source: str, target: str, relation: str) -> None:
        if source not in self._nodes or target not in self._nodes:
            return
        self._edges = [e for e in self._edges if not (e.source == source and e.target == target and e.relation == relation)]
        self._edges.append(GraphEdge(source=source, target=target, relation=relation))

    def apply_signal(self, signal: Signal) -> None:
        """All subsystem updates flow into the global graph."""
        ts = signal.timestamp.isoformat()
        kernel_node = "system:odin"
        self.upsert_node(kernel_node, "system", "ODIN Kernel", {"last_signal": signal.name})

        if signal.kind == SignalKind.WORKFLOW and signal.workflow_id:
            wid = f"workflow:{signal.workflow_id}"
            self.upsert_node(wid, "workflow", signal.workflow_id[:12], signal.payload)
            self.link("project:PROJECT_ODIN", wid, "executes")
            self.link(kernel_node, wid, "supervises")

        if signal.kind == SignalKind.MEMORY:
            mid = signal.payload.get("memory_id", str(uuid4())[:8])
            nid = f"memory:{mid}"
            self.upsert_node(nid, "memory", f"memory {mid}", signal.payload)
            self.link("project:PROJECT_ODIN", nid, "remembers")

        if signal.kind == SignalKind.DESKTOP:
            sid = f"session:{signal.correlation_id or 'desktop'}"
            self.upsert_node(sid, "desktop_state", "Desktop Session", {**signal.payload, "at": ts})
            self.link("user:default", sid, "active_on")

        if signal.kind == SignalKind.BROWSER:
            bid = f"browser:{signal.correlation_id or uuid4().hex[:8]}"
            self.upsert_node(bid, "browser_session", "Browser", signal.payload)
            self.link("project:PROJECT_ODIN", bid, "researches")

        if signal.kind == SignalKind.AGENT:
            aid = f"agent:{signal.source}"
            self.upsert_node(aid, "agent", str(signal.source), signal.payload)
            self.link(kernel_node, aid, "delegates")

        if signal.kind == SignalKind.TOOL:
            tid = f"tool:{signal.payload.get('tool', signal.name)}"
            self.upsert_node(tid, "tool", tid, signal.payload)
            if signal.workflow_id:
                self.link(f"workflow:{signal.workflow_id}", tid, "uses")

        if signal.kind == SignalKind.CONVERSATION:
            cid = signal.payload.get("session_id", signal.correlation_id or "conv")
            nid = f"conversation:{cid}"
            self.upsert_node(nid, "conversation", "Conversation", signal.payload)
            self.link("user:default", nid, "dialogues")

    def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    def related(self, node_id: str, depth: int = 1) -> list[GraphNode]:
        found: set[str] = {node_id}
        frontier = [node_id]
        for _ in range(depth):
            next_f: list[str] = []
            for e in self._edges:
                if e.source in frontier and e.target not in found:
                    found.add(e.target)
                    next_f.append(e.target)
                if e.target in frontier and e.source not in found:
                    found.add(e.source)
                    next_f.append(e.source)
            frontier = next_f
        return [self._nodes[n] for n in found if n in self._nodes]

    def snapshot(self) -> dict[str, Any]:
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "nodes": [n.model_dump(mode="json") for n in list(self._nodes.values())[:50]],
            "edges": [e.model_dump() for e in self._edges[:100]],
        }

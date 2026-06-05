"""Federation topology graph."""

from __future__ import annotations

from typing import Any


class FederationTopology:
    def __init__(self) -> None:
        self._edges: list[tuple[str, str, str]] = []
        self._modes = {"isolated", "trusted_cluster", "supervised_mesh", "research_mesh"}

    def link(self, a: str, b: str, *, kind: str = "peer") -> None:
        self._edges.append((a, b, kind))

    def snapshot(self) -> dict[str, Any]:
        nodes = {e[0] for e in self._edges} | {e[1] for e in self._edges}
        return {
            "edge_count": len(self._edges),
            "node_count": len(nodes),
            "edges": [{"from": a, "to": b, "kind": k} for a, b, k in self._edges[-50:]],
        }

    def is_valid_mode(self, mode: str) -> bool:
        return mode in self._modes

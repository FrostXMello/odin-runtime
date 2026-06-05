"""Pattern mining from execution history."""

from __future__ import annotations

from collections import Counter
from typing import Any

from odin_backend.core.cognition.clustering import cluster_by_key, top_clusters


def mine_tool_chains(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chains: Counter[str] = Counter()
    for e in events:
        tool = e.get("tool") or e.get("capability")
        if tool and e.get("success"):
            chains[str(tool)] += 1
    return [{"tool": k, "count": v} for k, v in chains.most_common(10)]


def mine_failure_clusters(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failed = [e for e in events if not e.get("success")]
    clusters = cluster_by_key(failed, "capability")
    return top_clusters(clusters)

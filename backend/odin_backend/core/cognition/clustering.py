"""Simple failure/success pattern clustering."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def cluster_by_key(items: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        clusters[str(item.get(key, "unknown"))].append(item)
    return dict(clusters)


def top_clusters(clusters: dict[str, list], *, limit: int = 5) -> list[dict[str, Any]]:
    ranked = sorted(clusters.items(), key=lambda x: -len(x[1]))
    return [{"key": k, "count": len(v), "samples": v[:3]} for k, v in ranked[:limit]]

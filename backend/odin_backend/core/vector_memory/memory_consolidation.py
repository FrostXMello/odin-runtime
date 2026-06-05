"""Long-term memory consolidation."""

from __future__ import annotations

from typing import Any


def compress_memories(entries: list[dict[str, Any]], *, max_entries: int = 100) -> dict[str, Any]:
    if len(entries) <= max_entries:
        return {"compressed": 0, "remaining": len(entries), "entries": entries}
    scored = sorted(entries, key=lambda e: e.get("importance", 0.5), reverse=True)
    kept = scored[:max_entries]
    pruned = len(entries) - len(kept)
    return {"compressed": pruned, "remaining": len(kept), "entries": kept}


def summarize_episodic(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    if not episodes:
        return {"summary": "", "count": 0}
    texts = [e.get("text", "")[:80] for e in episodes[:5]]
    return {"summary": " | ".join(texts), "count": len(episodes)}


def cluster_by_project(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    clusters: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        project = entry.get("metadata", {}).get("project", "default")
        clusters.setdefault(project, []).append(entry)
    return clusters

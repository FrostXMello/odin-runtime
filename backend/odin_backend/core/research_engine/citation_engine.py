"""Generate citations from sources."""

from __future__ import annotations

from typing import Any


def build_citations(sources: list[dict[str, Any]]) -> list[dict[str, str]]:
    citations: list[dict] = []
    for i, s in enumerate(sources, start=1):
        citations.append(
            {
                "ref": f"[{i}]",
                "url": s.get("url", ""),
                "title": s.get("title", "Untitled"),
            }
        )
    return citations

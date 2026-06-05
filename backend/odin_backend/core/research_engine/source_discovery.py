"""Discover candidate sources for a topic."""

from __future__ import annotations

from typing import Any

from odin_backend.core.knowledge.source_attribution import attribute_source


async def discover_sources(app: Any, *, topic: str) -> list[dict[str, Any]]:
    search = getattr(app, "web_access", None)
    if search:
        results = await search.search(topic)
        return results
    slug = topic.lower().replace(" ", "-")[:40]
    return [
        attribute_source(url=f"https://example.com/research/{slug}", title=f"Overview: {topic}", trust=0.6),
        attribute_source(url=f"https://docs.example.com/{slug}", title=f"Docs: {topic}", trust=0.7),
    ]

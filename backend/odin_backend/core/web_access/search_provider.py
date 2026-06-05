"""Search abstraction — local stub."""

from __future__ import annotations

from odin_backend.core.knowledge.source_attribution import attribute_source


async def search(topic: str) -> list[dict]:
    slug = topic.lower().replace(" ", "-")[:40]
    return [
        attribute_source(url=f"https://search.local/q/{slug}", title=f"Search: {topic}", trust=0.55),
    ]

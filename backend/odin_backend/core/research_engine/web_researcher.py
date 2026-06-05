"""Web research orchestration."""

from __future__ import annotations

from typing import Any

from odin_backend.core.research_engine.retrieval_pipeline import retrieve_sources
from odin_backend.core.research_engine.source_discovery import discover_sources
from odin_backend.core.research_engine.source_ranking import rank_sources


async def gather_evidence(app: Any, *, topic: str) -> list[dict[str, Any]]:
    discovered = await discover_sources(app, topic=topic)
    ranked = rank_sources(discovered, topic=topic)
    return await retrieve_sources(app, ranked)

"""Semantic memory — generalized operational knowledge."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognition.entities import MemoryEntity, MemoryEntityKind


def semantic_from_pattern(
    *,
    label: str,
    domain: str,
    confidence: float = 0.6,
    metadata: dict[str, Any] | None = None,
) -> MemoryEntity:
    return MemoryEntity(
        kind=MemoryEntityKind.SEMANTIC,
        label=label[:500],
        confidence=confidence,
        metadata={"domain": domain, **(metadata or {})},
    )

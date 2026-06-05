"""Procedural memory — successful strategies and workflows."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognition.entities import MemoryEntity, MemoryEntityKind


def procedural_from_strategy(
    *,
    strategy_kind: str,
    objective_domain: str,
    success_rate: float,
    metadata: dict[str, Any] | None = None,
) -> MemoryEntity:
    return MemoryEntity(
        kind=MemoryEntityKind.PROCEDURAL,
        label=f"{strategy_kind}:{objective_domain}",
        confidence=min(0.99, success_rate),
        metadata={"strategy": strategy_kind, "domain": objective_domain, **(metadata or {})},
    )

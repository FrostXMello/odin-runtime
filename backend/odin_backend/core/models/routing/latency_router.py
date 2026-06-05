"""Latency-aware model routing."""

from __future__ import annotations

from odin_backend.core.models.registry import LocalModelRegistry


class LatencyRouter:
    def __init__(self, registry: LocalModelRegistry) -> None:
        self._registry = registry

    def fastest(self, *, min_context: int = 0) -> str | None:
        profiles = self._registry.list_profiles()
        viable = [p for p in profiles if p.context_window >= min_context]
        if not viable:
            return profiles[0].name if profiles else None
        return sorted(viable, key=lambda p: p.avg_latency_ms or 9999)[0].name

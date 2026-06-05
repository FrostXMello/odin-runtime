"""Confidence-based model routing."""

from __future__ import annotations

from odin_backend.core.models.registry import LocalModelRegistry


class ConfidenceRouter:
    def __init__(self, registry: LocalModelRegistry) -> None:
        self._registry = registry

    def best_reliability(self) -> str | None:
        profiles = self._registry.list_profiles()
        if not profiles:
            return None
        return sorted(profiles, key=lambda p: -p.success_rate)[0].name

    def adjust_success(self, model_name: str, success: bool) -> None:
        prof = self._registry.get(model_name)
        if not prof:
            return
        delta = 0.05 if success else -0.08
        prof.success_rate = max(0.05, min(0.99, prof.success_rate + delta))

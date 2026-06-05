"""Select local models by task requirements."""

from __future__ import annotations

from typing import Any

from odin_backend.core.models.model_profiles import ModelCapabilityTag
from odin_backend.core.models.registry import LocalModelRegistry


class ModelSelector:
    def __init__(self, registry: LocalModelRegistry, *, app: Any | None = None) -> None:
        self._registry = registry
        self._app = app

    def select(
        self,
        *,
        task: str,
        context_tokens: int = 0,
        reasoning_depth: str = "normal",
        memory_pressure: float = 0.0,
    ) -> str:
        if task in ("route", "classify", "retry"):
            tag = ModelCapabilityTag.FAST
        elif task in ("embed", "rerank"):
            tag = ModelCapabilityTag.EMBEDDING
        elif task in ("reflect", "plan", "synthesize"):
            tag = ModelCapabilityTag.REASONING
        else:
            tag = ModelCapabilityTag.REASONING

        candidates = self._registry.by_capability(tag)
        if memory_pressure > 0.75:
            candidates = sorted(candidates, key=lambda p: p.ram_mb_estimate)
        elif reasoning_depth == "deep":
            candidates = sorted(candidates, key=lambda p: -p.context_window)
        else:
            candidates = sorted(candidates, key=lambda p: p.avg_latency_ms)

        viable = [c for c in candidates if c.context_window >= context_tokens]
        pool = viable or candidates or self._registry.list_profiles()
        if not pool:
            return "mock-reasoning"
        intel = getattr(self._app, "execution_intelligence", None) if self._app else None
        if intel and task == "plan":
            scores = intel.capability_scores()
            pool = sorted(pool, key=lambda p: -scores.get(p.name, {}).get("reliability", 0.5))
        return pool[0].name

"""Route inference requests to the active local provider."""

from __future__ import annotations

from typing import Any

from odin_backend.core.models.model_profiles import ModelCapabilityTag
from odin_backend.core.models.registry import LocalModelRegistry


class InferenceRouter:
    def __init__(self, registry: LocalModelRegistry) -> None:
        self._registry = registry

    def select_model(
        self,
        *,
        capability: ModelCapabilityTag,
        context_tokens: int = 0,
        prefer_low_latency: bool = False,
    ) -> str:
        candidates = self._registry.by_capability(capability)
        if not candidates:
            profiles = self._registry.list_profiles()
            return profiles[0].name if profiles else "mock-reasoning"
        viable = [c for c in candidates if c.context_window >= context_tokens or context_tokens == 0]
        pool = viable or candidates
        if prefer_low_latency:
            pool = sorted(pool, key=lambda p: p.avg_latency_ms)
        else:
            pool = sorted(pool, key=lambda p: -p.success_rate)
        return pool[0].name

    def route_payload(self, *, task_kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        tag_map = {
            "routing": ModelCapabilityTag.FAST,
            "classification": ModelCapabilityTag.CLASSIFICATION,
            "planning": ModelCapabilityTag.REASONING,
            "synthesis": ModelCapabilityTag.SYNTHESIS,
            "embedding": ModelCapabilityTag.EMBEDDING,
            "rerank": ModelCapabilityTag.RERANK,
            "reflection": ModelCapabilityTag.REASONING,
        }
        tag = tag_map.get(task_kind, ModelCapabilityTag.REASONING)
        model = self.select_model(
            capability=tag,
            context_tokens=payload.get("context_tokens", 0),
            prefer_low_latency=task_kind in ("routing", "classification"),
        )
        return {"model": model, "capability": tag.value, "task_kind": task_kind}

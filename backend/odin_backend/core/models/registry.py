"""Local model registry with capability tracking."""

from __future__ import annotations

from typing import Any

from odin_backend.config import Settings
from odin_backend.core.models.model_profiles import ModelCapabilityTag, ModelProfile, ModelProviderKind
from odin_backend.core.models.providers.base import LocalModelProvider
from odin_backend.core.models.providers.llamacpp import LlamaCppProvider
from odin_backend.core.models.providers.mlx import MLXProvider
from odin_backend.core.models.providers.mock import MockProvider
from odin_backend.core.models.providers.ollama import OllamaLocalProvider


class LocalModelRegistry:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._profiles: dict[str, ModelProfile] = {}
        self._providers: dict[str, LocalModelProvider] = {}
        self._active_provider = self._build_provider(settings.model_provider)
        self._seed_defaults()

    def _build_provider(self, name: str) -> LocalModelProvider:
        kind = name.lower()
        if kind == "ollama":
            return OllamaLocalProvider(self._settings)
        if kind == "llamacpp":
            return LlamaCppProvider(self._settings)
        if kind == "mlx":
            return MLXProvider(self._settings)
        return MockProvider()

    def _seed_defaults(self) -> None:
        defaults = [
            (self._settings.reasoning_model, [ModelCapabilityTag.REASONING, ModelCapabilityTag.SYNTHESIS]),
            (self._settings.fast_model, [ModelCapabilityTag.FAST, ModelCapabilityTag.CLASSIFICATION]),
            (self._settings.embedding_model, [ModelCapabilityTag.EMBEDDING, ModelCapabilityTag.RERANK]),
        ]
        provider_kind = ModelProviderKind(self._active_provider.name)
        for name, tags in defaults:
            self._profiles[name] = ModelProfile(
                name=name,
                provider=provider_kind,
                capability_tags=tags,
            )

    @property
    def provider(self) -> LocalModelProvider:
        return self._active_provider

    def register_profile(self, profile: ModelProfile) -> None:
        self._profiles[profile.name] = profile

    def get(self, name: str) -> ModelProfile | None:
        return self._profiles.get(name)

    def list_profiles(self) -> list[ModelProfile]:
        return list(self._profiles.values())

    def loaded_models(self) -> list[ModelProfile]:
        return [p for p in self._profiles.values() if p.loaded]

    def by_capability(self, tag: ModelCapabilityTag) -> list[ModelProfile]:
        return [p for p in self._profiles.values() if p.supports(tag)]

    def record_latency(self, name: str, latency_ms: float) -> None:
        prof = self._profiles.get(name)
        if not prof:
            return
        prof.avg_latency_ms = prof.avg_latency_ms * 0.8 + latency_ms * 0.2

    def snapshot(self) -> dict[str, Any]:
        return {
            "provider": self._active_provider.name,
            "models": [p.model_dump(mode="json") for p in self._profiles.values()],
            "loaded": [p.name for p in self.loaded_models()],
        }

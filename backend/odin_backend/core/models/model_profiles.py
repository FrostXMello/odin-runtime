"""Model capability profiles for local inference routing."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ModelProviderKind(StrEnum):
    OLLAMA = "ollama"
    LLAMA_CPP = "llamacpp"
    MLX = "mlx"
    MOCK = "mock"


class ModelCapabilityTag(StrEnum):
    REASONING = "reasoning"
    FAST = "fast"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    CLASSIFICATION = "classification"
    SYNTHESIS = "synthesis"


class ModelProfile(BaseModel):
    name: str
    provider: ModelProviderKind = ModelProviderKind.MOCK
    quantization: str = "none"
    context_window: int = 8192
    ram_mb_estimate: int = 4096
    vram_mb_estimate: int = 0
    capability_tags: list[ModelCapabilityTag] = Field(default_factory=list)
    avg_latency_ms: float = 0.0
    success_rate: float = 0.85
    loaded: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    def supports(self, tag: ModelCapabilityTag) -> bool:
        return tag in self.capability_tags

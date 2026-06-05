"""Mock provider for offline tests."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from odin_backend.core.models.model_profiles import (
    ModelCapabilityTag,
    ModelProfile,
    ModelProviderKind,
)
from odin_backend.core.models.providers.base import LocalModelProvider


class MockProvider(LocalModelProvider):
    name = "mock"

    def __init__(self) -> None:
        self._loaded: set[str] = set()
        self._cancelled: set[str] = set()

    async def health_check(self) -> dict[str, Any]:
        return {"healthy": True, "provider": self.name}

    async def list_models(self) -> list[str]:
        return ["mock-reasoning", "mock-fast", "mock-embed"]

    async def load_model(self, model_name: str) -> ModelProfile:
        self._loaded.add(model_name)
        tags = [ModelCapabilityTag.FAST]
        if "reason" in model_name:
            tags = [ModelCapabilityTag.REASONING, ModelCapabilityTag.SYNTHESIS]
        if "embed" in model_name:
            tags = [ModelCapabilityTag.EMBEDDING, ModelCapabilityTag.RERANK]
        return ModelProfile(
            name=model_name,
            provider=ModelProviderKind.MOCK,
            context_window=8192,
            ram_mb_estimate=512,
            capability_tags=tags,
            loaded=True,
        )

    async def unload_model(self, model_name: str) -> bool:
        self._loaded.discard(model_name)
        return True

    async def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        last = messages[-1].get("content", "") if messages else ""
        return f"[mock:{model}] Reasoned response for: {last[:120]}"

    async def stream_complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        text = await self.complete(model=model, messages=messages, temperature=temperature)
        for word in text.split():
            if asyncio.current_task() and asyncio.current_task().cancelled():
                break
            yield word + " "
            await asyncio.sleep(0)

    async def embed(self, *, model: str, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for t in texts:
            vec = [float((hash(t + str(i)) % 1000) / 1000.0) for i in range(16)]
            out.append(vec)
        return out

    def cancel(self, request_id: str) -> bool:
        self._cancelled.add(request_id)
        return True

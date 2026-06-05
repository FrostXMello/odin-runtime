"""Abstract local model provider."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

from odin_backend.core.models.model_profiles import ModelProfile


class LocalModelProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        ...

    @abstractmethod
    async def list_models(self) -> list[str]:
        ...

    @abstractmethod
    async def load_model(self, model_name: str) -> ModelProfile:
        ...

    @abstractmethod
    async def unload_model(self, model_name: str) -> bool:
        ...

    @abstractmethod
    async def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        ...

    @abstractmethod
    async def stream_complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        ...

    @abstractmethod
    async def embed(self, *, model: str, texts: list[str]) -> list[list[float]]:
        ...

    async def rerank(self, *, model: str, query: str, documents: list[str]) -> list[float]:
        """Default rerank via embedding cosine similarity."""
        q_emb = (await self.embed(model=model, texts=[query]))[0]
        doc_embs = await self.embed(model=model, texts=documents)
        scores: list[float] = []
        for d in doc_embs:
            scores.append(_cosine(q_emb, d))
        return scores

    def cancel(self, request_id: str) -> bool:
        return False


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

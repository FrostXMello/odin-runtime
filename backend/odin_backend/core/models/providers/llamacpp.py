"""llama.cpp HTTP server provider."""

from __future__ import annotations

from typing import Any, AsyncIterator

import httpx

from odin_backend.config import Settings
from odin_backend.core.models.model_profiles import (
    ModelCapabilityTag,
    ModelProfile,
    ModelProviderKind,
)
from odin_backend.core.models.providers.base import LocalModelProvider


class LlamaCppProvider(LocalModelProvider):
    name = "llamacpp"

    def __init__(self, settings: Settings) -> None:
        self._base = settings.model_base_url.rstrip("/")
        self._loaded: set[str] = set()

    async def health_check(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self._base}/health")
                return {"healthy": r.status_code == 200, "provider": self.name}
        except Exception as exc:
            return {"healthy": False, "provider": self.name, "error": str(exc)}

    async def list_models(self) -> list[str]:
        return list(self._loaded) or ["gguf-default"]

    async def load_model(self, model_name: str) -> ModelProfile:
        self._loaded.add(model_name)
        return ModelProfile(
            name=model_name,
            provider=ModelProviderKind.LLAMA_CPP,
            quantization="q4_k_m",
            context_window=4096,
            ram_mb_estimate=4096,
            capability_tags=[ModelCapabilityTag.REASONING],
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
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        body: dict[str, Any] = {"prompt": prompt, "temperature": temperature, "stream": False}
        if max_tokens:
            body["n_predict"] = max_tokens
        async with httpx.AsyncClient(timeout=180.0) as client:
            r = await client.post(f"{self._base}/completion", json=body)
            r.raise_for_status()
            return r.json().get("content", "")

    async def stream_complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        text = await self.complete(model=model, messages=messages, temperature=temperature)
        yield text

    async def embed(self, *, model: str, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        async with httpx.AsyncClient(timeout=60.0) as client:
            for text in texts:
                r = await client.post(f"{self._base}/embedding", json={"content": text})
                r.raise_for_status()
                out.append(r.json().get("embedding", []))
        return out

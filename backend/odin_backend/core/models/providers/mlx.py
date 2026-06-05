"""MLX provider for Apple Silicon local inference."""

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


class MLXProvider(LocalModelProvider):
    name = "mlx"

    def __init__(self, settings: Settings) -> None:
        self._base = settings.model_base_url.rstrip("/")
        self._loaded: set[str] = set()

    async def health_check(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self._base}/v1/models")
                return {"healthy": r.status_code == 200, "provider": self.name}
        except Exception as exc:
            return {"healthy": False, "provider": self.name, "error": str(exc)}

    async def list_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{self._base}/v1/models")
                r.raise_for_status()
                data = r.json().get("data", [])
                return [m.get("id", "") for m in data if m.get("id")]
        except Exception:
            return []

    async def load_model(self, model_name: str) -> ModelProfile:
        self._loaded.add(model_name)
        return ModelProfile(
            name=model_name,
            provider=ModelProviderKind.MLX,
            quantization="q4_k_m",
            context_window=8192,
            ram_mb_estimate=8192,
            vram_mb_estimate=0,
            capability_tags=[ModelCapabilityTag.REASONING, ModelCapabilityTag.SYNTHESIS],
            loaded=True,
            metadata={"platform": "apple_silicon"},
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
        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens:
            body["max_tokens"] = max_tokens
        async with httpx.AsyncClient(timeout=180.0) as client:
            r = await client.post(f"{self._base}/v1/chat/completions", json=body)
            r.raise_for_status()
            choices = r.json().get("choices", [])
            return choices[0].get("message", {}).get("content", "") if choices else ""

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
                r = await client.post(
                    f"{self._base}/v1/embeddings",
                    json={"model": model, "input": text},
                )
                r.raise_for_status()
                data = r.json().get("data", [{}])[0]
                out.append(data.get("embedding", []))
        return out

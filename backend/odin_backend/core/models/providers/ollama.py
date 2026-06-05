"""Ollama local model provider."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from odin_backend.config import Settings
from odin_backend.core.models.model_profiles import (
    ModelCapabilityTag,
    ModelProfile,
    ModelProviderKind,
)
from odin_backend.core.models.providers.base import LocalModelProvider


class OllamaLocalProvider(LocalModelProvider):
    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self._base = settings.model_base_url.rstrip("/")
        self._settings = settings
        self._loaded: set[str] = set()

    async def health_check(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self._base}/api/tags")
                return {"healthy": r.status_code == 200, "provider": self.name}
        except Exception as exc:
            return {"healthy": False, "provider": self.name, "error": str(exc)}

    async def list_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{self._base}/api/tags")
                r.raise_for_status()
                models = r.json().get("models", [])
                return [m.get("name", "") for m in models if m.get("name")]
        except Exception:
            return []

    async def load_model(self, model_name: str) -> ModelProfile:
        async with httpx.AsyncClient(timeout=120.0) as client:
            await client.post(f"{self._base}/api/pull", json={"name": model_name, "stream": False})
        self._loaded.add(model_name)
        tags = _infer_tags(model_name)
        return ModelProfile(
            name=model_name,
            provider=ModelProviderKind.OLLAMA,
            context_window=8192,
            ram_mb_estimate=6144,
            capability_tags=tags,
            loaded=True,
        )

    async def unload_model(self, model_name: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                await client.post(
                    f"{self._base}/api/generate",
                    json={"model": model_name, "keep_alive": 0},
                )
            self._loaded.discard(model_name)
            return True
        except Exception:
            return False

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
            "stream": False,
            "options": {"temperature": temperature},
        }
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        async with httpx.AsyncClient(timeout=180.0) as client:
            r = await client.post(f"{self._base}/api/chat", json=body)
            r.raise_for_status()
            return r.json().get("message", {}).get("content", "")

    async def stream_complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        body = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature},
        }
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream("POST", f"{self._base}/api/chat", json=body) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break

    async def embed(self, *, model: str, texts: list[str]) -> list[list[float]]:
        embed_model = model or self._settings.embedding_model
        out: list[list[float]] = []
        async with httpx.AsyncClient(timeout=120.0) as client:
            for text in texts:
                r = await client.post(
                    f"{self._base}/api/embeddings",
                    json={"model": embed_model, "prompt": text},
                )
                r.raise_for_status()
                out.append(r.json().get("embedding", []))
        return out


def _infer_tags(model_name: str) -> list[ModelCapabilityTag]:
    lower = model_name.lower()
    if "embed" in lower or "nomic" in lower:
        return [ModelCapabilityTag.EMBEDDING, ModelCapabilityTag.RERANK]
    if any(k in lower for k in ("phi", "mini", "tiny")):
        return [ModelCapabilityTag.FAST, ModelCapabilityTag.CLASSIFICATION]
    return [ModelCapabilityTag.REASONING, ModelCapabilityTag.SYNTHESIS]

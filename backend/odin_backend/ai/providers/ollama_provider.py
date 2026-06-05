"""Ollama local model provider."""

from typing import Any

import httpx

from odin_backend.ai.providers.base import AIProvider, CompletionRequest, CompletionResponse
from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self._base = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    @property
    def available(self) -> bool:
        return True  # checked lazily on request

    async def _ping(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self._base}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        if not await self._ping():
            raise RuntimeError("Ollama not available")

        model = request.model or self._model
        body: dict[str, Any] = {
            "model": model,
            "messages": request.messages,
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self._base}/api/chat", json=body)
            resp.raise_for_status()
            data = resp.json()
        content = data.get("message", {}).get("content", "")
        return CompletionResponse(content=content, model=model, raw=data)

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base}/api/embeddings",
                json={"model": self._model, "prompt": text},
            )
            resp.raise_for_status()
            return resp.json().get("embedding", [])

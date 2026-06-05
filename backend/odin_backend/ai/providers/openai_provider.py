"""OpenAI provider with retries and structured output support."""

import json
from typing import Any

import httpx

from odin_backend.ai.providers.base import AIProvider, CompletionRequest, CompletionResponse
from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"
MAX_RETRIES = 3


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._api_key = settings.openai_api_key
        self._base_url = "https://api.openai.com/v1"

    @property
    def available(self) -> bool:
        return bool(self._api_key)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        if not self.available:
            raise RuntimeError("OpenAI API key not configured")

        model = request.model or DEFAULT_MODEL
        body: dict[str, Any] = {
            "model": model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        if request.response_format:
            body["response_format"] = request.response_format

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(
                        f"{self._base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self._api_key}",
                            "Content-Type": "application/json",
                        },
                        json=body,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return CompletionResponse(
                        content=content,
                        model=model,
                        usage=data.get("usage", {}),
                        raw=data,
                    )
            except Exception as exc:
                last_error = exc
                logger.warning("openai_retry", attempt=attempt + 1, error=str(exc))
        raise RuntimeError(f"OpenAI completion failed: {last_error}")

    async def embed(self, text: str) -> list[float]:
        if not self.available:
            return []

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": EMBED_MODEL, "input": text},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]

    async def complete_json(self, request: CompletionRequest) -> dict[str, Any]:
        req = request.model_copy(
            update={"response_format": {"type": "json_object"}}
        )
        response = await self.complete(req)
        return json.loads(response.content)

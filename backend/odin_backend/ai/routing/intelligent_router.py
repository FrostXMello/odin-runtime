"""Intelligent model router — local vs cloud by task type."""

from enum import StrEnum

from odin_backend.ai.providers.base import CompletionRequest, CompletionResponse, ModelRole
from odin_backend.ai.providers.ollama_provider import OllamaProvider
from odin_backend.ai.providers.openai_provider import OpenAIProvider
from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class TaskComplexity(StrEnum):
    LIGHT = "light"
    MODERATE = "moderate"
    ADVANCED = "advanced"


class IntelligentModelRouter:
    """Routes by latency, privacy, complexity, and availability."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._openai = OpenAIProvider(settings)
        self._ollama = OllamaProvider(settings)

    def classify_task(self, messages: list[dict], *, role: ModelRole = ModelRole.REASONING) -> TaskComplexity:
        text = " ".join(m.get("content", "") for m in messages).lower()
        if role == ModelRole.REASONING or len(text) > 2000:
            return TaskComplexity.ADVANCED
        if any(w in text for w in ("plan", "workflow", "orchestrate", "design")):
            return TaskComplexity.ADVANCED
        if any(w in text for w in ("summarize", "short", "brief")):
            return TaskComplexity.LIGHT
        return TaskComplexity.MODERATE

    async def complete(
        self,
        request: CompletionRequest,
        *,
        role: ModelRole = ModelRole.REASONING,
        prefer_local: bool | None = None,
    ) -> CompletionResponse:
        complexity = self.classify_task(request.messages, role=role)
        use_local = prefer_local if prefer_local is not None else self._settings.prefer_local_for_summarization

        if complexity == TaskComplexity.LIGHT and use_local:
            try:
                return await self._ollama.complete(request)
            except Exception as exc:
                logger.debug("ollama_fallback_openai", error=str(exc))

        if complexity == TaskComplexity.ADVANCED and self._openai.available:
            return await self._openai.complete(request)

        if self._openai.available:
            return await self._openai.complete(request)

        return await self._ollama.complete(request)

    async def embed(self, text: str) -> list[float]:
        try:
            return await self._ollama.embed(text)
        except Exception:
            if self._openai.available:
                return await self._openai.embed(text)
            return []

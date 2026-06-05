"""Route requests to the best available provider."""

from odin_backend.ai.providers.base import AIProvider, CompletionRequest, CompletionResponse, ModelRole
from odin_backend.ai.providers.openai_provider import OpenAIProvider
from odin_backend.config import Settings


class ModelRouter:
    """Selects provider by role; extensible for Ollama/local."""

    def __init__(self, settings: Settings) -> None:
        self._openai = OpenAIProvider(settings)
        self._providers: list[AIProvider] = [self._openai]

    def get_provider(self, role: ModelRole = ModelRole.REASONING) -> AIProvider | None:
        if self._openai.available:
            return self._openai
        return None

    async def complete(
        self, request: CompletionRequest, role: ModelRole = ModelRole.REASONING
    ) -> CompletionResponse:
        provider = self.get_provider(role)
        if provider is None:
            raise RuntimeError("No AI provider available")
        return await provider.complete(request)

    async def embed(self, text: str) -> list[float]:
        provider = self.get_provider(ModelRole.EMBEDDING)
        if provider is None:
            return []
        return await provider.embed(text)

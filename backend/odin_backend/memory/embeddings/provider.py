"""Embedding provider — delegates to AI router."""

from odin_backend.ai.routing.router import ModelRouter


class EmbeddingProvider:
    def __init__(self, router: ModelRouter) -> None:
        self._router = router

    async def embed(self, text: str) -> list[float]:
        return await self._router.embed(text)

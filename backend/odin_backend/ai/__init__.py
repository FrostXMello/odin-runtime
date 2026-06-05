"""AI provider abstraction — swappable LLM backends."""

from odin_backend.ai.providers.base import AIProvider, CompletionRequest, CompletionResponse
from odin_backend.ai.routing.router import ModelRouter

__all__ = ["AIProvider", "CompletionRequest", "CompletionResponse", "ModelRouter"]

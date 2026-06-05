"""Local model provider adapters."""

from odin_backend.core.models.providers.base import LocalModelProvider
from odin_backend.core.models.providers.mock import MockProvider
from odin_backend.core.models.providers.ollama import OllamaLocalProvider

__all__ = ["LocalModelProvider", "MockProvider", "OllamaLocalProvider"]

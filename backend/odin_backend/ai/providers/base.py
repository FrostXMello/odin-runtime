"""Abstract AI provider — OpenAI, Ollama, local models implement this."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ModelRole(StrEnum):
    REASONING = "reasoning"
    FAST = "fast"
    EMBEDDING = "embedding"


class CompletionRequest(BaseModel):
    messages: list[dict[str, str]]
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int = 4096
    response_format: dict[str, Any] | None = None


class CompletionResponse(BaseModel):
    content: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)


class AIProvider(ABC):
    name: str

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        ...

    @property
    @abstractmethod
    def available(self) -> bool:
        ...

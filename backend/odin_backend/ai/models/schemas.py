"""Typed schemas for LLM structured outputs — streaming-ready."""

from typing import Any

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_tokens: int = 4096


class LLMPlanStep(BaseModel):
    step_id: int
    agent: str
    tool: str
    description: str = ""
    params: dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    depends_on: list[int] = Field(default_factory=list)


class LLMPlanResponse(BaseModel):
    objective: str
    steps: list[LLMPlanStep]

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

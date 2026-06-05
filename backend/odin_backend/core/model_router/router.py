"""ModelRouter — Gemini + local models unified for kernel inference."""

from enum import StrEnum

from pydantic import BaseModel, Field

from odin_backend.ai.providers.base import CompletionRequest, CompletionResponse, ModelRole
from odin_backend.ai.routing.intelligent_router import IntelligentModelRouter
from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class TaskModelType(StrEnum):
    PLANNING = "planning"
    REASONING = "reasoning"
    CODE = "code"
    AGENT = "agent"
    CONVERSATIONAL = "conversational"
    SUMMARIZATION = "summarization"


class RoutingResult(BaseModel):
    model_choice: str
    reasoning_response: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    provider: str = ""
    latency_ms: float = 0.0
    fallback_used: bool = False


class KernelModelRouter:
    """
    Select model per task type with fallback chain.

    Logical models: Gemini, DeepSeek R1/Coder, Qwen2.5, Llama 3.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._intelligent = IntelligentModelRouter(settings)

    def select_model(self, task_type: TaskModelType) -> str:
        mapping = {
            TaskModelType.PLANNING: self._settings.model_gemini,
            TaskModelType.REASONING: self._settings.model_gemini,
            TaskModelType.CODE: self._settings.model_deepseek_coder,
            TaskModelType.AGENT: self._settings.model_qwen,
            TaskModelType.CONVERSATIONAL: self._settings.model_llama,
            TaskModelType.SUMMARIZATION: self._settings.model_llama,
        }
        return mapping.get(task_type, self._settings.model_gemini)

    def _fallback_chain(self, task_type: TaskModelType) -> list[str]:
        primary = self.select_model(task_type)
        if task_type in (TaskModelType.PLANNING, TaskModelType.REASONING):
            return [primary, self._settings.model_deepseek_r1, self._settings.ollama_model]
        if task_type == TaskModelType.CODE:
            return [primary, self._settings.model_deepseek_r1, self._settings.ollama_model]
        return [primary, self._settings.ollama_model]

    async def route_and_complete(
        self,
        messages: list[dict[str, str]],
        task_type: TaskModelType,
        *,
        temperature: float = 0.2,
    ) -> RoutingResult:
        import time

        chain = self._fallback_chain(task_type)
        last_error: str | None = None
        for idx, model_name in enumerate(chain):
            start = time.perf_counter()
            try:
                request = CompletionRequest(
                    messages=messages,
                    model=model_name,
                    temperature=temperature,
                )
                role = ModelRole.REASONING
                if task_type == TaskModelType.SUMMARIZATION:
                    role = ModelRole.FAST
                response = await self._intelligent.complete(
                    request,
                    role=role,
                    prefer_local=model_name == self._settings.ollama_model,
                )
                elapsed = (time.perf_counter() - start) * 1000
                confidence = 0.92 if idx == 0 else max(0.5, 0.85 - idx * 0.15)
                return RoutingResult(
                    model_choice=response.model or model_name,
                    reasoning_response=response.content,
                    confidence_score=confidence,
                    provider=response.model,
                    latency_ms=round(elapsed, 2),
                    fallback_used=idx > 0,
                )
            except Exception as exc:
                last_error = str(exc)
                logger.warning("model_route_fallback", model=model_name, error=last_error)

        return RoutingResult(
            model_choice="rule-based",
            reasoning_response=last_error or "No model available",
            confidence_score=0.3,
            provider="fallback",
            fallback_used=True,
        )

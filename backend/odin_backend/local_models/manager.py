"""LocalModelManager — Ollama lifecycle, scheduling, GPU awareness."""

import asyncio
import time
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.ai.providers.ollama_provider import OllamaProvider
from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class InferencePriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class InferenceJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    model: str
    prompt_preview: str = ""
    priority: InferencePriority = InferencePriority.NORMAL
    status: str = "queued"  # queued | running | completed | cancelled
    created_at: float = Field(default_factory=time.time)


class LocalModelManager:
    SUPPORTED_MODELS = ("llama3.2", "qwen2.5", "mistral", "deepseek-r1", "llama3.1")

    def __init__(self, settings: Settings, event_bus: EventBus) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._ollama = OllamaProvider(settings)
        self._loaded_models: dict[str, float] = {}  # model -> last_used timestamp
        self._queue: asyncio.PriorityQueue[tuple[int, InferenceJob]] = asyncio.PriorityQueue()
        self._active_job: InferenceJob | None = None
        self._gpu_available: bool | None = None

    @property
    def available(self) -> bool:
        return self._ollama.available

    async def list_models(self) -> list[str]:
        if self._ollama.available:
            return list(self.SUPPORTED_MODELS)
        return []

    async def warm_model(self, model: str | None = None) -> dict[str, Any]:
        model = model or self._settings.ollama_model
        self._loaded_models[model] = time.time()
        await self._emit("model_warmed", {"model": model})
        return {"model": model, "status": "warm", "available": self.available}

    async def unload_inactive(self, max_idle_seconds: int = 600) -> list[str]:
        now = time.time()
        unloaded = []
        for model, last_used in list(self._loaded_models.items()):
            if now - last_used > max_idle_seconds:
                del self._loaded_models[model]
                unloaded.append(model)
        if unloaded:
            await self._emit("models_unloaded", {"models": unloaded})
        return unloaded

    def gpu_status(self) -> dict[str, Any]:
        # Lightweight probe — full GPU metrics via optional deps later
        return {
            "gpu_detected": self._gpu_available,
            "loaded_models": list(self._loaded_models.keys()),
            "ollama_available": self.available,
        }

    async def schedule_inference(
        self,
        prompt: str,
        *,
        model: str | None = None,
        priority: InferencePriority = InferencePriority.NORMAL,
    ) -> InferenceJob:
        job = InferenceJob(
            model=model or self._settings.ollama_model,
            prompt_preview=prompt[:120],
            priority=priority,
        )
        prio_val = {InferencePriority.HIGH: 0, InferencePriority.NORMAL: 1, InferencePriority.LOW: 2}[
            priority
        ]
        await self._queue.put((prio_val, job))
        await self._emit("inference_queued", job.model_dump())
        return job

    async def cancel_inference(self, job_id: str) -> bool:
        if self._active_job and self._active_job.id == job_id:
            self._active_job.status = "cancelled"
            return True
        return False

    def runtime_status(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "base_url": self._settings.ollama_base_url,
            "default_model": self._settings.ollama_model,
            "loaded_models": list(self._loaded_models.keys()),
            "queue_size": self._queue.qsize(),
            "active_job": self._active_job.model_dump() if self._active_job else None,
            "gpu": self.gpu_status(),
        }

    async def _emit(self, action: str, payload: dict[str, Any]) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.LOCAL_MODEL_UPDATED,
                source=AgentId.ODIN,
                payload={"action": action, **payload},
            )
        )

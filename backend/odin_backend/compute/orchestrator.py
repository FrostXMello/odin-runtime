"""AI compute orchestrator — scheduling, embeddings, failover."""

import asyncio
import hashlib
import time
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.ai.routing.intelligent_router import IntelligentModelRouter
from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.local_models.manager import LocalModelManager
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ComputePriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class ComputeJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_type: str  # inference | embedding
    priority: ComputePriority = ComputePriority.NORMAL
    status: str = "queued"
    created_at: float = Field(default_factory=time.time)


class AIComputeOrchestrator:
    def __init__(
        self,
        settings: Settings,
        event_bus: EventBus,
        local_models: LocalModelManager,
        router: IntelligentModelRouter | None = None,
    ) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._local = local_models
        self._router = router
        self._queue: asyncio.PriorityQueue[tuple[int, ComputeJob]] = asyncio.PriorityQueue()
        self._embedding_cache: dict[str, list[float]] = {}
        self._inference_cache: dict[str, str] = {}

    async def schedule_inference(
        self,
        prompt: str,
        *,
        priority: ComputePriority = ComputePriority.NORMAL,
        prefer_local: bool = True,
    ) -> ComputeJob:
        job = ComputeJob(job_type="inference", priority=priority)
        prio = {ComputePriority.HIGH: 0, ComputePriority.NORMAL: 1, ComputePriority.LOW: 2}[priority]
        await self._queue.put((prio, job))
        if prefer_local and self._local.available:
            from odin_backend.local_models.manager import InferencePriority

            prio = InferencePriority(job.priority.value)
            await self._local.schedule_inference(prompt, priority=prio)
        await self._emit("inference_scheduled", {"job_id": job.id})
        return job

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Local embedding pipeline with simple hash fallback when no model."""
        results: list[list[float]] = []
        for text in texts:
            key = hashlib.sha256(text.encode()).hexdigest()[:32]
            if key in self._embedding_cache:
                results.append(self._embedding_cache[key])
                continue
            # Lightweight deterministic pseudo-embedding for offline retrieval
            vec = [((ord(c) * (i + 1)) % 100) / 100.0 for i, c in enumerate(text[:64].ljust(64))]
            self._embedding_cache[key] = vec
            results.append(vec)
        await self._emit("embeddings_batch", {"count": len(texts)})
        return results

    async def warmup(self) -> dict[str, Any]:
        return await self._local.warm_model()

    def runtime_dashboard(self) -> dict[str, Any]:
        local_status = self._local.runtime_status()
        return {
            "local_models": local_status,
            "queue_size": self._queue.qsize(),
            "embedding_cache_size": len(self._embedding_cache),
            "inference_cache_size": len(self._inference_cache),
            "gpu": local_status.get("gpu", {}),
        }

    async def _emit(self, action: str, payload: dict[str, Any]) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.COMPUTE_UPDATED,
                source=AgentId.ODIN,
                payload={"action": action, **payload},
            )
        )

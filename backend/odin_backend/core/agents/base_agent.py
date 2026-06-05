"""Cognitive agent abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentReasoningStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_kind: str
    content: str
    confidence: float = 0.7
    model: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CognitiveAgent(ABC):
    kind: str = "base"

    def __init__(self, app: Any) -> None:
        self._app = app

    @abstractmethod
    async def run(self, *, objective: str, mission_id: str | None = None, context: dict[str, Any] | None = None) -> AgentReasoningStep:
        ...

    async def _infer(self, prompt: str, *, task_kind: str, mission_id: str | None = None) -> tuple[str, str]:
        from odin_backend.core.models.routing.capability_router import ModelCapabilityRouter
        from odin_backend.core.models.routing.model_selector import ModelSelector

        selector = ModelSelector(self._app.model_manager.registry, app=self._app)
        router = ModelCapabilityRouter(selector)
        route = router.route(self.kind)
        model = route["model"]
        text = await self._app.model_manager.runtime.infer(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            task_kind=task_kind,
            mission_id=mission_id,
        )
        return str(text), model

    def _emit_trace(self, kind_name: str, payload: dict, *, mission_id: str | None = None) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        trace_payload = {**payload, "agent": self.kind}
        if mission_id:
            trace_payload["mission_id"] = mission_id
        obs.tracer.record(
            kind,
            message=kind_name,
            payload=trace_payload,
            component="cognitive_agent",
        )

"""Route cognitive tasks to model capabilities."""

from __future__ import annotations

from odin_backend.core.models.model_profiles import ModelCapabilityTag
from odin_backend.core.models.routing.model_selector import ModelSelector


class ModelCapabilityRouter:
    def __init__(self, selector: ModelSelector) -> None:
        self._selector = selector

    def route(self, agent_kind: str, *, context_tokens: int = 0) -> dict[str, str]:
        task_map = {
            "planner": "plan",
            "researcher": "research",
            "critic": "reflect",
            "verifier": "classify",
            "memory": "embed",
            "synthesizer": "synthesize",
            "coordinator": "route",
        }
        task = task_map.get(agent_kind, "plan")
        model = self._selector.select(task=task, context_tokens=context_tokens)
        tag = ModelCapabilityTag.REASONING.value
        if task in ("route", "classify", "retry"):
            tag = ModelCapabilityTag.FAST.value
        if task in ("embed", "rerank"):
            tag = ModelCapabilityTag.EMBEDDING.value
        return {"model": model, "task": task, "capability": tag}

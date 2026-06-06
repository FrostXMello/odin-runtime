"""Multi-model cognitive pipeline orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.local_ai.cognitive_pipeline.adaptive_context_window import compress_context
from odin_backend.core.local_ai.cognitive_pipeline.cognition_budget_allocator import allocate_budget
from odin_backend.core.local_ai.cognitive_pipeline.hierarchical_inference import hierarchical_infer
from odin_backend.core.local_ai.cognitive_pipeline.realtime_model_scheduler import schedule_realtime
from odin_backend.core.local_ai.cognitive_pipeline.streaming_reasoning_pipeline import stream_reason


class CognitivePipelineRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._inferences = 0

    async def infer(self, *, prompt: str, complexity: float = 0.5, stream: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_pipeline_enabled", False):
            return {"accepted": False, "reason": "cognitive_pipeline_disabled"}
        vram = getattr(self._app.settings, "local_ai_vram_mb", 4096)
        on_battery = getattr(self._app.settings, "on_battery", False)
        budget = allocate_budget(vram_mb=vram, on_battery=on_battery)
        schedule = schedule_realtime(latency_ms=50 if complexity < 0.5 else 200)
        compressed = compress_context(text=prompt, max_tokens=budget["context_tokens"])
        if stream:
            chunks = stream_reason(prompt=compressed["text"], depth="light" if complexity < 0.6 else "deep")
            result = {"streamed": True, "chunks": chunks}
        else:
            result = hierarchical_infer(prompt=compressed["text"], complexity=complexity)
        self._inferences += 1
        return {"accepted": True, "budget": budget, "schedule": schedule, "compressed": compressed, "result": result}

    def snapshot(self) -> dict[str, Any]:
        return {"inferences": self._inferences}

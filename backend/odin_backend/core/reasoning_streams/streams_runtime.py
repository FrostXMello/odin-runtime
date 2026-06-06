"""Visual reasoning streams orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.reasoning_streams.cognitive_heatmaps import heatmap
from odin_backend.core.reasoning_streams.live_decision_graph import graph
from odin_backend.core.reasoning_streams.mission_visualizer import visualize
from odin_backend.core.reasoning_streams.reasoning_pipeline import pipeline
from odin_backend.core.reasoning_streams.stream_summarizer import summarize
from odin_backend.core.reasoning_streams.thought_renderer import render


class ReasoningStreamsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._items: list[str] = []

    async def push(self, *, thought: str, steps: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "reasoning_streams_enabled", False):
            return {"accepted": False, "reason": "reasoning_streams_disabled"}
        self._items.append(thought)
        r = render(text=thought)
        pipe = pipeline(steps=steps or ["observe", "reason", "respond"])
        self._emit("reasoning_stream_updated", {"items": len(self._items)})
        return {
            "accepted": True,
            "rendered": r,
            "pipeline": pipe,
            "summary": summarize(items=self._items),
            "heatmap": heatmap(zones={"cognition": 0.7, "memory": 0.4, "execution": 0.5}),
            "decisions": graph(decisions=steps or ["observe", "act"]),
            "transparent": True,
        }

    async def mission(self, *, mission_id: str, state: str = "active") -> dict[str, Any]:
        viz = visualize(mission_id=mission_id, state=state)
        return {"accepted": True, "mission": viz}

    def snapshot(self) -> dict[str, Any]:
        return {"items": len(self._items)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="reasoning_streams")

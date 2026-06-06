"""Live cognitive visualization orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_visualization.agent_activity_visualizer import agent_graph
from odin_backend.core.cognitive_visualization.cognition_graph import build_graph
from odin_backend.core.cognitive_visualization.execution_flow_map import flow_map
from odin_backend.core.cognitive_visualization.live_reasoning_map import reasoning_map
from odin_backend.core.cognitive_visualization.memory_activity_map import memory_map
from odin_backend.core.cognitive_visualization.runtime_heatmap import heatmap
from odin_backend.core.cognitive_visualization.strategy_visualizer import strategy_tree
from odin_backend.core.cognitive_visualization.thought_stream import ThoughtStream


class CognitiveVisualizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._stream = ThoughtStream()

    async def render(self, *, thought: str = "", steps: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_visualization_enabled", False):
            return {"accepted": False, "reason": "cognitive_visualization_disabled"}
        steps = steps or ["observe", "reason", "respond"]
        if thought:
            item = self._stream.push(thought)
            self._emit("thought_generated", item)
        graph = build_graph(nodes=steps)
        reasoning = reasoning_map(steps=steps)
        self._emit("reasoning_stream_updated", {"nodes": len(graph["nodes"])})
        return {
            "accepted": True,
            "graph": graph,
            "reasoning_map": reasoning,
            "execution_flow": flow_map(steps=steps),
            "memory_activity": memory_map(threads=3),
            "agents": agent_graph(agents=["planner", "debugger"]),
            "strategy": strategy_tree(root=steps[0], branches=steps[1:]),
            "heatmap": heatmap(load=0.35),
            "thought_stream": self._stream.snapshot(),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"thought_stream": self._stream.snapshot()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_visualization")

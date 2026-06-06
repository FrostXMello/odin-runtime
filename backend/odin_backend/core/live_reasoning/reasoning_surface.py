"""Live streaming reasoning surface (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.live_reasoning.attention_heatmap import heatmap
from odin_backend.core.live_reasoning.cognitive_diff import diff_branches
from odin_backend.core.live_reasoning.live_chain_tracker import LiveChainTracker
from odin_backend.core.live_reasoning.reasoning_layers import layer_stack
from odin_backend.core.live_reasoning.reasoning_timeline import ReasoningTimeline
from odin_backend.core.live_reasoning.token_stream_visualizer import tokenize_stream


class LiveReasoningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._chains = LiveChainTracker()
        self._timeline = ReasoningTimeline()
        self._profile = "balanced"

    async def render(self, *, thought: str = "", branch_b: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "live_reasoning_enabled", False):
            return {"accepted": False, "reason": "live_reasoning_disabled"}
        if hasattr(self._app, "reasoning_streams"):
            await self._app.reasoning_streams.push(thought=thought or "live reasoning")
        layers = layer_stack(thought or "analyzing")
        tokens = tokenize_stream(thought or "…")
        self._chains.push(thought or "step", confidence=0.72)
        hm = heatmap(layers)
        branch = diff_branches(thought, branch_b) if branch_b else None
        self._timeline.record("render", {"tokens": len(tokens)})
        recalls = {}
        if hasattr(self._app, "memory_threads"):
            recalls = await self._app.memory_threads.recall()
        self._emit("reasoning_branch_rendered", {"tokens": len(tokens), "layers": len(layers)})
        caps = {"ultra_light": 15, "balanced": 30, "immersive": 45, "cinematic": 60}
        return {
            "accepted": True,
            "tokens": tokens,
            "layers": layers,
            "heatmap": hm,
            "chain": self._chains.snapshot(),
            "branch_compare": branch,
            "memory_recalls": recalls,
            "hallucination_warning": False,
            "fps_cap": caps.get(self._profile, 30),
            "lazy_render": True,
            "playback": self._timeline.playback(),
        }

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("ultra_light", "balanced", "immersive", "cinematic"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile}

    def snapshot(self) -> dict[str, Any]:
        return {"profile": self._profile, "chain_len": len(self._chains.snapshot())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_reasoning")

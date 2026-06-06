"""Realtime cognitive streams (Prompt 48)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_streams.attention_streams import stream as attention_stream
from odin_backend.core.cognitive_streams.contextual_stream_router import route
from odin_backend.core.cognitive_streams.live_memory_streams import replay
from odin_backend.core.cognitive_streams.reasoning_snapshots import ReasoningSnapshots
from odin_backend.core.cognitive_streams.reflection_streams import reflect
from odin_backend.core.cognitive_streams.stream_compression import compress


class CognitiveStreamsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._thoughts: list[str] = []
        self._snaps = ReasoningSnapshots()
        self._profile = "balanced"

    async def push(self, *, thought: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_streams_enabled", False):
            return {"accepted": False, "reason": "cognitive_streams_disabled"}
        self._thoughts.append(thought[:200])
        compressed = compress(self._thoughts)
        if len(compressed) < len(self._thoughts):
            self._emit("thought_stream_compressed", {"before": len(self._thoughts), "after": len(compressed)})
        snap = self._snaps.capture(thought)
        if hasattr(self._app, "reasoning_streams"):
            await self._app.reasoning_streams.push(thought=thought)
        return {
            "accepted": True,
            "stream": compressed,
            "snapshot": snap,
            "attention": attention_stream(focus=thought),
            "channels": route(profile=self._profile),
            "low_resource": self._profile in ("survival", "lightweight"),
        }

    async def reflect_stream(self, *, summary: str) -> dict[str, Any]:
        r = reflect(summary=summary)
        mem = replay(self._thoughts)
        return {"accepted": True, "reflection": r, "memory_replay": mem}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("survival", "lightweight", "balanced", "immersive", "overnight", "cinematic"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile}

    def snapshot(self) -> dict[str, Any]:
        return {"thoughts": len(self._thoughts)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_streams")

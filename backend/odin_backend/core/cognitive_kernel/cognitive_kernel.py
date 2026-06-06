"""Persistent cognitive kernel orchestrator (Prompt 48)."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

from odin_backend.core.cognitive_kernel.continuity_engine import rehydrate
from odin_backend.core.cognitive_kernel.context_prioritizer import prioritize
from odin_backend.core.cognitive_kernel.kernel_metrics import metrics
from odin_backend.core.cognitive_kernel.kernel_state import load_state, save_state
from odin_backend.core.cognitive_kernel.operator_state import OperatorState
from odin_backend.core.cognitive_kernel.persistent_attention import attention_vector
from odin_backend.core.cognitive_kernel.reasoning_scheduler import schedule

PROFILES = ("survival", "lightweight", "balanced", "immersive", "overnight", "cinematic")


class CognitiveKernelRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._id = str(uuid4())
        self._profile = "balanced"
        self._ticks = 0
        self._operator = OperatorState()
        self._path = "./data/cognitive_kernel.json"

    async def heartbeat(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_kernel_enabled", False):
            return {"accepted": False, "reason": "cognitive_kernel_disabled"}
        self._ticks += 1
        attn = attention_vector(focus=self._operator._focus)
        if hasattr(self._app, "cognitive_daemon"):
            await self._app.cognitive_daemon.tick(idle_s=0)
        self._emit("kernel_attention_shifted", attn)
        caps = {"survival": 10, "lightweight": 15, "balanced": 30, "immersive": 45, "overnight": 8, "cinematic": 60}
        return {
            "accepted": True,
            "kernel_id": self._id,
            "tick": self._ticks,
            "attention": attn,
            "interval_s": schedule(self._profile),
            "metrics": metrics(ticks=self._ticks, memory_links=0),
            "fps_cap": caps.get(self._profile, 30),
            "orchestration_layer": True,
        }

    async def prioritize_context(self, *, contexts: list[dict] | None = None) -> dict[str, Any]:
        ctx = prioritize(contexts=contexts or [{"weight": 0.5, "source": "workspace"}])
        return {"accepted": True, "contexts": ctx}

    async def restore(self) -> dict[str, Any]:
        restored = load_state(path=self._path)
        continuity = await rehydrate(self._app)
        if restored.get("restored"):
            self._emit("cross_runtime_sync_completed", {"kernel_id": self._id})
        return {"accepted": True, "kernel": restored, "continuity": continuity}

    async def focus(self, *, focus: str) -> dict[str, Any]:
        hit = self._operator.shift(focus)
        self._emit("kernel_attention_shifted", hit)
        return {"accepted": True, **hit}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in PROFILES:
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        save_state(path=self._path, state={"profile": profile, "kernel_id": self._id})
        return {"accepted": True, "profile": profile, "pause_heavy": profile == "survival"}

    def snapshot(self) -> dict[str, Any]:
        return {"kernel_id": self._id, "profile": self._profile, "ticks": self._ticks}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_kernel")

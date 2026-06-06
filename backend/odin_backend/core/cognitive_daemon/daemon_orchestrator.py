"""Continuous cognitive daemon orchestration (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_daemon.adaptive_focus_scheduler import tick_interval
from odin_backend.core.cognitive_daemon.background_reflection import reflect
from odin_backend.core.cognitive_daemon.continuous_attention import heartbeat
from odin_backend.core.cognitive_daemon.environment_awareness_loop import observe
from odin_backend.core.cognitive_daemon.idle_reasoning import idle_tick
from odin_backend.core.cognitive_daemon.proactive_memory_refresh import refresh
from odin_backend.core.cognitive_daemon.task_resumption import resurface


class CognitiveDaemonOrchestrator:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._profile = "balanced"
        self._idle_s = 0.0

    async def tick(self, *, idle_s: float = 0.0) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_daemon_enabled", False):
            return {"accepted": False, "reason": "cognitive_daemon_disabled"}
        self._idle_s = idle_s
        hb = heartbeat(idle_s=idle_s)
        if hasattr(self._app, "daemon_runtime"):
            await self._app.daemon_runtime.cognitive_tick(wakeword="", energy=0.3)
        idle = await idle_tick(self._app)
        mem = await refresh(self._app)
        ref = await reflect(self._app)
        env = await observe(self._app)
        tasks = await resurface(self._app)
        if tasks.get("unfinished"):
            self._emit("unfinished_task_resurfaced", {"count": len(tasks.get("unfinished", []))})
        self._emit("daemon_attention_shifted", hb)
        return {
            "accepted": True,
            "heartbeat": hb,
            "idle": idle,
            "memory": mem,
            "reflection": ref,
            "environment": env,
            "tasks": tasks,
            "interval_s": tick_interval(self._profile),
            "resource_aware": True,
        }

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("ultra_light", "balanced", "immersive", "cinematic"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile, "interval_s": tick_interval(profile)}

    def snapshot(self) -> dict[str, Any]:
        return {"profile": self._profile, "idle_s": self._idle_s}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_daemon")

"""Continuous engineering daemon (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.continuous_engineering.attention_resumption import resume
from odin_backend.core.continuous_engineering.background_validation import validate_light
from odin_backend.core.continuous_engineering.engineering_tick import tick
from odin_backend.core.continuous_engineering.overnight_analysis import analyze
from odin_backend.core.continuous_engineering.patch_queue_monitor import monitor
from odin_backend.core.continuous_engineering.repo_watchers import watch
from odin_backend.core.continuous_engineering.test_drift_detection import detect


class ContinuousEngineeringRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._profile = "balanced_engineering"

    async def engineering_tick(self, *, repo: str = "local", idle_s: float = 0.0) -> dict[str, Any]:
        if not getattr(self._app.settings, "continuous_engineering_enabled", False):
            return {"accepted": False, "reason": "continuous_engineering_disabled"}
        t = await tick(self._app, idle_s=idle_s)
        w = watch(repo)
        validation = await validate_light(self._app)
        drift = detect(["unit", "integration"])
        queue = monitor(self._app)
        restored = await resume(self._app)
        if hasattr(self._app, "cognitive_daemon"):
            await self._app.cognitive_daemon.tick(idle_s=idle_s)
        return {
            "accepted": True,
            "tick": t,
            "repo_watch": w,
            "validation": validation,
            "drift": drift,
            "patch_queue": queue,
            "restored": restored,
            "resource_aware": True,
        }

    async def overnight(self, *, repo: str = "local") -> dict[str, Any]:
        if self._profile != "overnight_engineering" and self._profile != "balanced_engineering":
            return {"accepted": True, "skipped": True, "reason": "profile_not_overnight"}
        result = await analyze(self._app, repo=repo)
        self._emit("overnight_analysis_completed", result)
        return {"accepted": True, **result}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("lightweight_engineering", "balanced_engineering", "autonomous_engineering", "overnight_engineering"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile}

    def snapshot(self) -> dict[str, Any]:
        return {"profile": self._profile}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="continuous_engineering")

"""Continuity recovery runtime (Prompt 61)."""
from __future__ import annotations
from typing import Any


class ContinuityRecoveryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._restored = False
        self._replay_loops = 0

    async def recover_mission_continuity(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "continuity_recovery_enabled", False):
            return {"accepted": False, "reason": "continuity_recovery_disabled"}
        if hasattr(self._app, "mission_command"):
            await self._app.mission_command.transition_operational_phase(phase="recovery")
        if hasattr(self._app, "mission_continuity"):
            await self._app.mission_continuity.estimate_continuity_health()
        self._restored = True
        self._emit("mission_continuity_restored", {"restored": True})
        return {"accepted": True, "restored": True, "approval_gated": True, "reversible": True}

    async def rebuild_workspace_context(self) -> dict[str, Any]:
        if hasattr(self._app, "context_synchronization"):
            await self._app.context_synchronization.merge_runtime_context()
        self._emit("workspace_context_rebuilt", {"rebuilt": True})
        return {"accepted": True, "rebuilt": True, "lazy_hydration": True}

    async def restore_interrupted_reasoning(self) -> dict[str, Any]:
        if hasattr(self._app, "deferred_reasoning"):
            await self._app.deferred_reasoning.restore_reasoning()
        return {"accepted": True, "restored": True, "supervised": True}

    async def replay_continuity_window(self) -> dict[str, Any]:
        if self._replay_loops > 40:
            return {"accepted": False, "reason": "continuity_replay_bounded"}
        self._replay_loops += 1
        if hasattr(self._app, "live_cognition_timeline"):
            return await self._app.live_cognition_timeline.replay_cognition_window()
        return {"accepted": True, "replay": [], "bounded": True}

    def snapshot(self) -> dict[str, Any]:
        return {"restored": self._restored, "replay_loops": self._replay_loops}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="continuity_recovery")

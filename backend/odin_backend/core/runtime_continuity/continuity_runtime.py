"""Runtime continuity orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.runtime_continuity.cognition_resume import CognitionResume
from odin_backend.core.runtime_continuity.continuity_recovery import recover_sessions
from odin_backend.core.runtime_continuity.long_term_context import LongTermContext
from odin_backend.core.runtime_continuity.operator_identity import OperatorIdentity
from odin_backend.core.runtime_continuity.persistent_sessions import PersistentSessionStore
from odin_backend.core.runtime_continuity.runtime_state_snapshots import RuntimeStateSnapshots
from odin_backend.core.runtime_continuity.temporal_memory_windows import TemporalMemoryWindows


class ContinuityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._sessions = PersistentSessionStore(app.settings)
        self._snapshots = RuntimeStateSnapshots(app.settings)
        self._context = LongTermContext()
        self._windows = TemporalMemoryWindows()
        self._resume = CognitionResume()
        self._operator = OperatorIdentity()

    async def connect(self) -> None:
        await self._sessions.connect()
        await self._snapshots.connect()
        if getattr(self._app.settings, "runtime_continuity_enabled", False):
            recovered = await recover_sessions(self._sessions, self._snapshots)
            if recovered["sessions_restored"] or recovered["behavioral_restored"]:
                self._emit("continuity_restored", recovered)

    async def disconnect(self) -> None:
        await self._snapshots.disconnect()
        await self._sessions.disconnect()

    async def checkpoint(self, *, state: dict, kind: str = "behavioral") -> dict[str, Any]:
        snap = await self._snapshots.capture(kind=kind, state=state)
        await self._sessions.save(operator_id=self._operator.operator_id, state=state)
        return snap

    async def defer_reasoning(self, *, kind: str, payload: dict) -> dict[str, Any]:
        return self._resume.defer(kind=kind, payload=payload)

    async def snapshot(self) -> dict[str, Any]:
        sessions = await self._sessions.list_active()
        return {
            "operator": self._operator.model_dump(),
            "active_sessions": len(sessions),
            "deferred_cognition": len(self._resume.pending()),
            "context_windows": len(self._context.list_all()),
            "temporal_windows": self._windows.snapshot(),
        }

    def missions_for(self, mission_id: str) -> dict[str, Any]:
        pending = [d for d in self._resume.pending() if d.get("payload", {}).get("mission_id") == mission_id]
        return {"mission_id": mission_id, "deferred": pending}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="runtime_continuity")

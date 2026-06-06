"""Persistent cognitive core orchestrator."""
from __future__ import annotations

import time
from typing import Any

import aiosqlite

from odin_backend.core.persistent_cognition.cognition_recovery import recover
from odin_backend.core.persistent_cognition.cognition_state_store import SqliteTable
from odin_backend.core.persistent_cognition.cognitive_resume import resume
from odin_backend.core.persistent_cognition.continuity_checkpointing import checkpoint
from odin_backend.core.persistent_cognition.daemon_snapshots import snapshot as daemon_snapshot
from odin_backend.core.persistent_cognition.deferred_intentions import DeferredIntentions
from odin_backend.core.persistent_cognition.long_running_threads import LongRunningThreads
from odin_backend.core.persistent_cognition.session_rehydration import rehydrate


class PersistentCognitionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._path = app.settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None
        self._state: SqliteTable | None = None
        self._checkpoints: SqliteTable | None = None
        self._threads = LongRunningThreads()
        self._intentions = DeferredIntentions()

    async def _ensure(self) -> None:
        if self._db:
            return
        self._db = await aiosqlite.connect(self._path)
        self._state = SqliteTable(self._db, "persistent_cognition_state")
        self._checkpoints = SqliteTable(self._db, "cognition_checkpoints")
        await self._state.ensure()
        await self._checkpoints.ensure()

    async def checkpoint(self, *, state: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "persistent_cognition_enabled", False):
            return {"accepted": False, "reason": "persistent_cognition_disabled"}
        await self._ensure()
        payload = {"created_at": time.time(), **(state or {"active": True})}
        cp = checkpoint(state=payload)
        assert self._checkpoints is not None
        await self._checkpoints.insert({**cp, **payload})
        assert self._state is not None
        await self._state.insert(payload)
        self._emit("cognition_checkpoint_created", cp)
        return {"accepted": True, "checkpoint": cp}

    async def rehydrate_session(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "persistent_cognition_enabled", False):
            return {"accepted": False, "reason": "persistent_cognition_disabled"}
        await self._ensure()
        assert self._state is not None
        recent = await self._state.recent(limit=1)
        snap = recent[0] if recent else {}
        rh = rehydrate(snapshot=snap)
        if hasattr(self._app, "daemon_runtime"):
            ds = daemon_snapshot(uptime_s=self._app.daemon_runtime._uptime_s, idle=self._app.daemon_runtime._idle)
            rh["daemon"] = ds
        self._emit("session_rehydrated", rh)
        return {"accepted": True, **rh}

    async def defer_intention(self, *, intention: str) -> dict[str, Any]:
        item = self._intentions.defer(intention)
        assert self._state is not None
        await self._ensure()
        await self._state.insert({"intention": item})
        return {"accepted": True, "intention": item}

    async def resume_cognition(self) -> dict[str, Any]:
        await self._ensure()
        assert self._checkpoints is not None
        cps = await self._checkpoints.recent(limit=5)
        rec = recover(checkpoints=cps)
        r = resume(chains=cps)
        return {"accepted": True, "recovery": rec, "resume": r}

    def snapshot(self) -> dict[str, Any]:
        return {"intentions": len(self._intentions.pending()), "sqlite": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="persistent_cognition")

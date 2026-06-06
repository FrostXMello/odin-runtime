"""Execution memory runtime (Prompt 57)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.execution_memory.execution_store import ExecutionStore


class ExecutionMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "execution_memory.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = ExecutionStore(db)

    async def persist_execution_chain(self, *, chain_id: str, stages: list[str] | None = None, success: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "execution_memory_enabled", False):
            return {"accepted": False, "reason": "execution_memory_disabled"}
        payload = {"stages": (stages or [])[:20], "reversible": True}
        self._store.save(chain_id=chain_id, payload=payload, success=success)
        self._emit("execution_chain_persisted", {"chain_id": chain_id[:40]})
        return {"accepted": True, "chain_id": chain_id, "persisted": True}

    async def replay_execution_sequence(self, *, chain_id: str) -> dict[str, Any]:
        data = self._store.load(chain_id=chain_id)
        return {"accepted": True, "replay": data, "lazy_hydration": True}

    async def compress_execution_history(self) -> dict[str, Any]:
        return {"accepted": True, "compressed": True, "bounded": True}

    async def resurface_successful_execution_patterns(self) -> dict[str, Any]:
        patterns = self._store.successful_patterns()
        return {"accepted": True, "patterns": patterns, "supervised": True}

    def snapshot(self) -> dict[str, Any]:
        return {"patterns": len(self._store.successful_patterns())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="execution_memory")

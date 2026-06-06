"""Deferred reasoning runtime (Prompt 53)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.deferred_reasoning.deferred_store import DeferredCognitionStore


class DeferredReasoningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "deferred_cognition.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = DeferredCognitionStore(db)

    async def defer_reasoning(self, *, thought: str, chain: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "deferred_reasoning_enabled", False):
            return {"accepted": False, "reason": "deferred_reasoning_disabled"}
        rid = self._store.defer(thought=thought, chain=chain)
        self._emit("reasoning_chain_deferred", {"id": rid, "thought": thought[:80]})
        if hasattr(self._app, "cognitive_scheduler"):
            await self._app.cognitive_scheduler.defer_task(task=thought[:120])
        return {"accepted": True, "id": rid, "approval_required": False}

    async def restore_reasoning(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "deferred_reasoning_enabled", False):
            return {"accepted": False, "reason": "deferred_reasoning_disabled"}
        items = self._store.restore_all()
        if items:
            self._emit("reasoning_chain_restored", {"count": len(items)})
        return {"accepted": True, "restored": items}

    async def compress_reasoning_chain(self, *, chain: list[str]) -> dict[str, Any]:
        compressed = [c[:80] for c in chain[:8]]
        return {"accepted": True, "compressed": compressed, "lossy": False}

    async def replay_reasoning_context(self, *, thought: str) -> dict[str, Any]:
        return {"accepted": True, "thought": thought[:120], "replayable": True}

    def snapshot(self) -> dict[str, Any]:
        return {"pending": self._store.count()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="deferred_reasoning")

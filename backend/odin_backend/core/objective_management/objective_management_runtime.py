"""Objective management runtime (Prompt 55)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.objective_management.objective_store import ObjectiveStore


class ObjectiveManagementRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "objectives.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = ObjectiveStore(db)

    async def create_objective_tree(self, *, root: str, children: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "objective_management_enabled", False):
            return {"accepted": False, "reason": "objective_management_disabled"}
        payload = {"root": root[:120], "children": (children or [])[:20], "approval_checkpoints": True}
        self._store.save(objective_id=root[:80], payload=payload, progress=0.0)
        self._emit("objective_tree_created", {"root": root[:60]})
        return {"accepted": True, "objective": payload, "supervised": True}

    async def update_objective_progress(self, *, objective_id: str, progress: float) -> dict[str, Any]:
        data = self._store.load(objective_id=objective_id)
        if not data:
            return {"accepted": False, "reason": "objective_not_found"}
        self._store.save(objective_id=objective_id, payload={k: v for k, v in data.items() if k not in ("objective_id", "progress")}, progress=progress)
        self._emit("objective_progress_updated", {"objective_id": objective_id[:60], "progress": progress})
        return {"accepted": True, "objective_id": objective_id, "progress": progress}

    async def detect_stalled_objectives(self) -> dict[str, Any]:
        stalled = [o for o in self._store.list_active() if o.get("progress", 0) < 0.05]
        if stalled:
            self._emit("stalled_objective_detected", {"count": len(stalled)})
        return {"accepted": True, "stalled": stalled[:10], "bounded": True}

    async def restore_objective_chain(self) -> dict[str, Any]:
        active = self._store.list_active(limit=5)
        return {"accepted": True, "chain": [o.get("objective_id") for o in active], "approval_gated": True}

    async def summarize_active_objectives(self) -> dict[str, Any]:
        active = self._store.list_active()
        return {"accepted": True, "objectives": active, "count": len(active)}

    def snapshot(self) -> dict[str, Any]:
        return {"active_count": len(self._store.list_active())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="objective_management")

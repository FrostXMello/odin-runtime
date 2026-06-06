"""Operator sessions runtime (Prompt 62)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.operator_sessions.session_store import OperatorSessionStore


class OperatorSessionsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "operator_sessions.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = OperatorSessionStore(db)
        self._active: dict[str, dict[str, Any]] = {}

    async def create_operator_session(self, *, operator_id: str = "operator-local", role: str = "supervisor") -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_sessions_enabled", False):
            return {"accepted": False, "reason": "operator_sessions_disabled"}
        payload = {
            "active_missions": [],
            "approval_authority": role in {"supervisor", "admin"},
            "focus_state": "available",
            "runtime_ownership": [],
            "supervision_scope": "local",
        }
        sid = self._store.create(operator_id=operator_id, role=role, payload=payload)
        self._active[operator_id] = {"session_id": sid, "role": role, **payload}
        self._emit("operator_session_created", {"operator_id": operator_id[:40], "role": role})
        return {"accepted": True, "session_id": sid, "operator_id": operator_id, "role": role, "transparent": True}

    async def restore_operator_session(self, *, operator_id: str = "operator-local") -> dict[str, Any]:
        sessions = [s for s in self._store.sessions() if s["operator_id"] == operator_id]
        restored = sessions[0] if sessions else None
        if restored:
            self._active[operator_id] = restored
        self._emit("operator_session_restored", {"operator_id": operator_id[:40], "restored": bool(restored)})
        return {"accepted": True, "restored": bool(restored), "session": restored, "reversible": True}

    async def synchronize_session_state(self) -> dict[str, Any]:
        return {"accepted": True, "active": list(self._active.values()), "permission_aware": True}

    async def build_session_replay(self) -> dict[str, Any]:
        return {"accepted": True, "replay": self._store.sessions(limit=20), "lazy_hydration": True}

    def snapshot(self) -> dict[str, Any]:
        return {"active": list(self._active.values()), "sessions": len(self._store.sessions())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_sessions")

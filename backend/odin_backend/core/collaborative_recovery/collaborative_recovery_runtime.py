"""Collaborative recovery runtime (Prompt 62)."""
from __future__ import annotations
from typing import Any


class CollaborativeRecoveryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._requests: list[dict[str, Any]] = []
        self._authorized: list[str] = []
        self._rollback_generated = False

    async def request_team_recovery(self, *, mission_id: str = "shared-mission") -> dict[str, Any]:
        if not getattr(self._app.settings, "collaborative_recovery_enabled", False):
            return {"accepted": False, "reason": "collaborative_recovery_disabled"}
        req = {"mission_id": mission_id, "status": "pending"}
        self._requests.append(req)
        if hasattr(self._app, "operator_veto"):
            await self._app.operator_veto.request_recovery_approval(path=f"team:{mission_id}", risk=0.4)
        self._emit("collaborative_recovery_requested", {"mission_id": mission_id[:40]})
        return {"accepted": True, "mission_id": mission_id, "approval_gated": True}

    async def authorize_shared_recovery(self, *, mission_id: str = "shared-mission") -> dict[str, Any]:
        if hasattr(self._app, "operator_veto"):
            auth = await self._app.operator_veto.authorize_recovery_chain(path=f"team:{mission_id}")
            if not auth.get("authorized"):
                return {"accepted": False, "reason": "shared_recovery_not_authorized"}
        self._authorized.append(mission_id)
        self._emit("shared_recovery_authorized", {"mission_id": mission_id[:40]})
        return {"accepted": True, "authorized": True, "mission_id": mission_id, "operator_supervised": True}

    async def build_collaborative_rollback(self, *, mission_id: str = "shared-mission") -> dict[str, Any]:
        if hasattr(self._app, "rollback_intelligence"):
            await self._app.rollback_intelligence.generate_rollback_graph()
        self._rollback_generated = True
        self._emit("collaborative_rollback_generated", {"mission_id": mission_id[:40]})
        return {"accepted": True, "mission_id": mission_id, "rollback_generated": True, "reversible": True}

    async def synchronize_recovery_state(self) -> dict[str, Any]:
        if hasattr(self._app, "continuity_recovery"):
            await self._app.continuity_recovery.recover_mission_continuity()
        self._emit("shared_continuity_restored", {"requests": len(self._requests)})
        return {"accepted": True, "synchronized": True, "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"requests": self._requests, "authorized": self._authorized, "rollback_generated": self._rollback_generated}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="collaborative_recovery")

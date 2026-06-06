"""Delegation engine runtime (Prompt 62)."""
from __future__ import annotations
from typing import Any


class DelegationEngineRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._delegations: dict[str, dict[str, Any]] = {}
        self._replay_loops = 0

    async def delegate_execution(self, *, task_id: str = "task-local", operator_id: str = "operator-local") -> dict[str, Any]:
        if not getattr(self._app.settings, "delegation_engine_enabled", False):
            return {"accepted": False, "reason": "delegation_engine_disabled"}
        authority = await self.validate_operator_authority(operator_id=operator_id)
        if not authority.get("valid"):
            return {"accepted": False, "reason": "authority_denied", "approval_gated": True}
        self._delegations[task_id] = {"task_id": task_id, "operator_id": operator_id, "status": "delegated"}
        self._emit("delegation_chain_created", {"task_id": task_id[:40], "operator_id": operator_id[:40]})
        return {"accepted": True, "task_id": task_id, "operator_id": operator_id, "approval_gated": True}

    async def revoke_delegation(self, *, task_id: str = "task-local") -> dict[str, Any]:
        delegation = self._delegations.get(task_id)
        if delegation:
            delegation["status"] = "revoked"
        return {"accepted": True, "task_id": task_id, "revoked": bool(delegation), "reversible": True}

    async def validate_operator_authority(self, *, operator_id: str = "operator-local") -> dict[str, Any]:
        valid = True
        if hasattr(self._app, "operator_sessions"):
            state = await self._app.operator_sessions.synchronize_session_state()
            active = state.get("active", [])
            valid = not active or any(s.get("operator_id") == operator_id or s.get("approval_authority") for s in active)
        self._emit("delegation_authority_validated", {"operator_id": operator_id[:40], "valid": valid})
        return {"accepted": True, "valid": valid, "permission_aware": True}

    async def replay_delegation_chain(self) -> dict[str, Any]:
        if self._replay_loops > 40:
            return {"accepted": False, "reason": "delegation_replay_bounded"}
        self._replay_loops += 1
        return {"accepted": True, "delegations": list(self._delegations.values()), "lazy_hydration": True}

    def snapshot(self) -> dict[str, Any]:
        return {"delegations": list(self._delegations.values()), "replay_loops": self._replay_loops}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="delegation_engine")

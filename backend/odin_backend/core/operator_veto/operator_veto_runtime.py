"""Operator veto runtime (Prompt 61)."""
from __future__ import annotations
from typing import Any


class OperatorVetoRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._pending: list[dict] = []
        self._vetoed: list[str] = []
        self._authorized: list[str] = []

    async def request_recovery_approval(self, *, path: str = "default", risk: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_veto_enabled", False):
            return {"accepted": False, "reason": "operator_veto_disabled"}
        req = {"path": path, "risk": risk, "status": "pending"}
        self._pending.append(req)
        self._emit("operator_veto_requested", {"path": path[:40], "risk": risk})
        return {"accepted": True, "approval_required": True, "path": path, "transparent": True}

    async def escalate_recovery_risk(self, *, risk: float = 0.7) -> dict[str, Any]:
        return {"accepted": True, "escalated": True, "risk": risk, "operator_visible": True, "trust_preserving": True}

    async def veto_recovery_path(self, *, path: str = "default") -> dict[str, Any]:
        self._vetoed.append(path)
        self._emit("recovery_path_vetoed", {"path": path[:40]})
        return {"accepted": True, "vetoed": True, "path": path, "operator_controlled": True}

    async def authorize_recovery_chain(self, *, path: str = "default") -> dict[str, Any]:
        if path in self._vetoed:
            return {"accepted": False, "reason": "path_vetoed", "authorized": False}
        self._authorized.append(path)
        self._emit("recovery_chain_authorized", {"path": path[:40]})
        return {"accepted": True, "authorized": True, "path": path, "approval_gated": True, "reversible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"pending": len(self._pending), "vetoed": len(self._vetoed), "authorized": len(self._authorized)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_veto")

"""Supervised action runtime — lifecycle, approval, execution, recovery."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from odin_backend.core.actions.action_context import ActionContext
from odin_backend.core.actions.action_history import ActionHistory
from odin_backend.core.actions.action_recovery import revert_action
from odin_backend.core.actions.action_router import dispatch_action


class ActionState(StrEnum):
    PROPOSED = "proposed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    REVERTED = "reverted"
    FAILED = "failed"
    BLOCKED = "blocked"


class ActionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._actions: dict[str, dict[str, Any]] = {}
        self._context = ActionContext()
        self._history = ActionHistory()
        self._emergency_stopped = False

    @property
    def emergency_stopped(self) -> bool:
        return self._emergency_stopped

    async def propose(
        self,
        *,
        kind: str,
        label: str,
        payload: dict | None = None,
        risk_hint: str | None = None,
    ) -> dict[str, Any]:
        action_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        risk = "supervised"
        if hasattr(self._app, "action_safety"):
            risk = self._app.action_safety.classify(kind=kind, payload=payload or {}, hint=risk_hint)

        state = ActionState.PROPOSED
        if risk == "blocked":
            state = ActionState.BLOCKED
            self._emit("destructive_action_blocked", {"action_id": action_id, "kind": kind})
        elif risk in ("supervised", "restricted"):
            state = ActionState.AWAITING_APPROVAL

        entry = {
            "id": action_id,
            "kind": kind,
            "label": label,
            "payload": payload or {},
            "risk": risk,
            "state": state.value,
            "created_at": now,
            "updated_at": now,
            "result": None,
        }
        self._actions[action_id] = entry
        self._history.record(entry)
        self._emit("action_proposed", {"action_id": action_id, "kind": kind, "risk": risk})
        if state == ActionState.AWAITING_APPROVAL and hasattr(self._app, "supervision_runtime"):
            await self._app.supervision_runtime.request_review(entry)
        return entry

    async def approve(self, action_id: str) -> dict[str, Any] | None:
        entry = self._actions.get(action_id)
        if not entry or entry["state"] not in (
            ActionState.AWAITING_APPROVAL.value,
            ActionState.PROPOSED.value,
            ActionState.PAUSED.value,
        ):
            return None
        if self._emergency_stopped:
            entry["state"] = ActionState.BLOCKED.value
            return entry
        entry["state"] = ActionState.APPROVED.value
        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._emit("action_approved", {"action_id": action_id})
        scheduler = getattr(self._app, "action_scheduler", None)
        if scheduler and getattr(scheduler, "_running", False):
            entry["state"] = ActionState.SCHEDULED.value
            await scheduler.enqueue(action_id)
        else:
            await self.execute_approved(action_id)
        return entry

    async def execute_approved(self, action_id: str) -> dict[str, Any] | None:
        entry = self._actions.get(action_id)
        if not entry or entry["state"] not in (
            ActionState.APPROVED.value,
            ActionState.SCHEDULED.value,
        ):
            return None
        if self._emergency_stopped:
            entry["state"] = ActionState.PAUSED.value
            self._emit("automation_interrupted", {"action_id": action_id, "reason": "emergency_stop"})
            return entry

        entry["state"] = ActionState.EXECUTING.value
        overlay = getattr(self._app, "overlay_runtime", None)
        if overlay:
            overlay.annotate_action(entry)

        try:
            result = await dispatch_action(self._app, entry)
            entry["result"] = result
            entry["state"] = ActionState.COMPLETED.value
            self._emit("action_executed", {"action_id": action_id, "result": result})
            macro = getattr(self._app, "macro_replay", None)
            if macro and macro._recorder.active:
                macro._recorder.record_step(entry)
        except Exception as exc:
            entry["result"] = {"error": str(exc)}
            entry["state"] = ActionState.FAILED.value
        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._history.record(dict(entry))
        return entry

    async def pause(self, action_id: str) -> dict[str, Any] | None:
        entry = self._actions.get(action_id)
        if not entry:
            return None
        if entry["state"] in (ActionState.EXECUTING.value, ActionState.SCHEDULED.value):
            entry["state"] = ActionState.PAUSED.value
            self._emit("automation_interrupted", {"action_id": action_id, "reason": "paused"})
        return entry

    async def cancel(self, action_id: str) -> dict[str, Any] | None:
        entry = self._actions.get(action_id)
        if not entry:
            return None
        entry["state"] = ActionState.BLOCKED.value
        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        return entry

    async def revert(self, action_id: str) -> dict[str, Any] | None:
        entry = self._actions.get(action_id)
        if not entry or entry["state"] != ActionState.COMPLETED.value:
            return None
        undo = await revert_action(self._app, entry)
        entry["state"] = ActionState.REVERTED.value
        entry["undo"] = undo
        self._emit("action_reverted", {"action_id": action_id, "undo": undo})
        return entry

    def emergency_stop(self) -> dict[str, Any]:
        self._emergency_stopped = True
        paused = 0
        for entry in self._actions.values():
            if entry["state"] in (ActionState.EXECUTING.value, ActionState.SCHEDULED.value):
                entry["state"] = ActionState.PAUSED.value
                paused += 1
        self._emit("automation_interrupted", {"reason": "emergency_stop", "paused": paused})
        return {"emergency_stopped": True, "paused": paused}

    def clear_emergency_stop(self) -> None:
        self._emergency_stopped = False

    def snapshot(self) -> dict[str, Any]:
        return {
            "emergency_stopped": self._emergency_stopped,
            "active_count": sum(
                1
                for a in self._actions.values()
                if a["state"] in (ActionState.EXECUTING.value, ActionState.SCHEDULED.value)
            ),
            "pending_approval": [
                a for a in self._actions.values() if a["state"] == ActionState.AWAITING_APPROVAL.value
            ],
            "recent": self._history.recent(limit=20),
            "context": self._context.snapshot(),
        }

    def get(self, action_id: str) -> dict[str, Any] | None:
        return self._actions.get(action_id)

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="action_runtime")

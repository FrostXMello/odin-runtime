"""Human collaboration runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.collaboration.approval_flows import ApprovalFlow
from odin_backend.core.collaboration.collaborative_reasoning import CollaborativeReasoning
from odin_backend.core.collaboration.human_feedback import HumanFeedbackStore
from odin_backend.core.collaboration.shared_context import SharedContext


class CollaborationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._context = SharedContext()
        self._approvals = ApprovalFlow()
        self._feedback = HumanFeedbackStore()
        self._reasoning = CollaborativeReasoning()

    async def request_approval(self, *, action: str, detail: str, mission_id: str | None = None) -> dict:
        entry = self._approvals.request(action=action, detail=detail, mission_id=mission_id)
        self._emit("approval_requested", entry)
        return entry

    async def resolve_approval(self, approval_id: str, *, approved: bool, feedback: str = "") -> dict | None:
        entry = self._approvals.resolve(approval_id, approved=approved, feedback=feedback)
        if entry:
            self._emit("collaboration_feedback_received", entry)
            self._feedback.record(kind="approval", value=1.0 if approved else -0.5, note=feedback)
        return entry

    def record_feedback(self, *, kind: str, value: float, note: str = "") -> None:
        self._feedback.record(kind=kind, value=value, note=note)
        self._emit("collaboration_feedback_received", {"kind": kind, "value": value})

    def snapshot(self) -> dict[str, Any]:
        return {
            "shared_context": self._context.snapshot(),
            "pending_approvals": self._approvals.pending(),
            "approval_history": self._approvals.history(),
            "feedback": self._feedback.recent(),
            "reasoning_sessions": self._reasoning.list_sessions(),
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="collaboration_runtime")

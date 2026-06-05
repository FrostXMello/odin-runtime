"""Supervision runtime — approval modes and review queue."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from odin_backend.core.supervision.action_review import ActionReviewQueue
from odin_backend.core.supervision.execution_watchdog import ExecutionWatchdog
from odin_backend.core.supervision.intervention_manager import InterventionManager
from odin_backend.core.supervision.live_confirmation import LiveConfirmation


class ApprovalMode(StrEnum):
    MANUAL_EVERY_STEP = "manual_every_step"
    MILESTONE_BASED = "milestone_based"
    SUPERVISED_BATCH = "supervised_batch"
    TRUSTED_WORKFLOW = "trusted_workflow"
    SIMULATION_ONLY = "simulation_only"


class SupervisionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        mode = getattr(app.settings, "approval_mode", ApprovalMode.MANUAL_EVERY_STEP.value)
        try:
            self._mode = ApprovalMode(mode)
        except ValueError:
            self._mode = ApprovalMode.MANUAL_EVERY_STEP
        self._reviews = ActionReviewQueue()
        self._confirmations = LiveConfirmation()
        self._interventions = InterventionManager()
        self._watchdog = ExecutionWatchdog(app)

    @property
    def mode(self) -> ApprovalMode:
        return self._mode

    async def request_review(self, action: dict[str, Any]) -> dict[str, Any]:
        entry = self._reviews.enqueue(action)
        if hasattr(self._app, "collaboration_runtime"):
            await self._app.collaboration_runtime.request_approval(
                action=action.get("kind", "action"),
                detail=action.get("label", ""),
            )
        return entry

    def snapshot(self) -> dict[str, Any]:
        return {
            "mode": self._mode.value,
            "pending_reviews": self._reviews.pending(),
            "interventions": self._interventions.recent(),
            "watchdog": self._watchdog.status(),
        }

"""Strict mission and task lifecycle state machines."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.models.mission import MissionLifecycle
from odin_backend.models.task_graph import TaskNodeStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class InvalidTransitionError(Exception):
    def __init__(self, entity: str, from_state: str, to_state: str) -> None:
        super().__init__(f"Invalid {entity} transition: {from_state} -> {to_state}")
        self.from_state = from_state
        self.to_state = to_state


# Extend mission lifecycle with strict orchestration states (values preserved in model enum)
# Legacy values remain on MissionLifecycle enum in models/mission.py — migration maps them.

MISSION_TRANSITIONS: dict[MissionLifecycle, frozenset[MissionLifecycle]] = {
    MissionLifecycle.QUEUED: frozenset(
        {MissionLifecycle.PLANNING, MissionLifecycle.APPROVAL_REQUIRED, MissionLifecycle.CANCELLED}
    ),
    MissionLifecycle.PLANNING: frozenset(
        {MissionLifecycle.PLANNED, MissionLifecycle.FAILED, MissionLifecycle.CANCELLED}
    ),
    MissionLifecycle.PLANNED: frozenset(
        {
            MissionLifecycle.DISPATCHED,
            MissionLifecycle.APPROVAL_REQUIRED,
            MissionLifecycle.BLOCKED,
            MissionLifecycle.CANCELLED,
            MissionLifecycle.FAILED,
        }
    ),
    MissionLifecycle.APPROVAL_REQUIRED: frozenset(
        {MissionLifecycle.PLANNED, MissionLifecycle.DISPATCHED, MissionLifecycle.CANCELLED}
    ),
    MissionLifecycle.DISPATCHED: frozenset(
        {MissionLifecycle.RUNNING, MissionLifecycle.BLOCKED, MissionLifecycle.CANCELLED, MissionLifecycle.FAILED}
    ),
    MissionLifecycle.RUNNING: frozenset(
        {
            MissionLifecycle.BLOCKED,
            MissionLifecycle.RETRYING,
            MissionLifecycle.ESCALATED,
            MissionLifecycle.COMPLETED,
            MissionLifecycle.FAILED,
            MissionLifecycle.CANCELLED,
        }
    ),
    MissionLifecycle.BLOCKED: frozenset(
        {MissionLifecycle.RUNNING, MissionLifecycle.RETRYING, MissionLifecycle.ESCALATED, MissionLifecycle.CANCELLED}
    ),
    MissionLifecycle.RETRYING: frozenset(
        {MissionLifecycle.RUNNING, MissionLifecycle.FAILED, MissionLifecycle.ESCALATED}
    ),
    MissionLifecycle.ESCALATED: frozenset(
        {MissionLifecycle.RUNNING, MissionLifecycle.CANCELLED, MissionLifecycle.FAILED}
    ),
    MissionLifecycle.COMPLETED: frozenset({MissionLifecycle.ARCHIVED}),
    MissionLifecycle.FAILED: frozenset({MissionLifecycle.ARCHIVED, MissionLifecycle.QUEUED}),
    MissionLifecycle.CANCELLED: frozenset({MissionLifecycle.ARCHIVED}),
    MissionLifecycle.ARCHIVED: frozenset(),
    # Legacy bridges
    MissionLifecycle.CREATED: frozenset({MissionLifecycle.PLANNING, MissionLifecycle.QUEUED, MissionLifecycle.CANCELLED}),
    MissionLifecycle.ACTIVE: frozenset(
        {MissionLifecycle.RUNNING, MissionLifecycle.DISPATCHED, MissionLifecycle.BLOCKED, MissionLifecycle.COMPLETED}
    ),
    MissionLifecycle.WAITING: frozenset({MissionLifecycle.RUNNING, MissionLifecycle.BLOCKED, MissionLifecycle.CANCELLED}),
}

TASK_TRANSITIONS: dict[TaskNodeStatus, frozenset[TaskNodeStatus]] = {
    TaskNodeStatus.PENDING: frozenset(
        {TaskNodeStatus.READY, TaskNodeStatus.SKIPPED, TaskNodeStatus.BLOCKED, TaskNodeStatus.FAILED}
    ),
    TaskNodeStatus.READY: frozenset({TaskNodeStatus.ASSIGNED, TaskNodeStatus.SKIPPED, TaskNodeStatus.BLOCKED}),
    TaskNodeStatus.ASSIGNED: frozenset({TaskNodeStatus.EXECUTING, TaskNodeStatus.BLOCKED, TaskNodeStatus.FAILED}),
    TaskNodeStatus.EXECUTING: frozenset(
        {TaskNodeStatus.RUNNING, TaskNodeStatus.COMPLETE, TaskNodeStatus.FAILED, TaskNodeStatus.BLOCKED, TaskNodeStatus.PENDING}
    ),
    TaskNodeStatus.RUNNING: frozenset(
        {TaskNodeStatus.EXECUTING, TaskNodeStatus.COMPLETE, TaskNodeStatus.FAILED, TaskNodeStatus.BLOCKED}
    ),
    TaskNodeStatus.BLOCKED: frozenset({TaskNodeStatus.READY, TaskNodeStatus.PENDING, TaskNodeStatus.SKIPPED}),
    TaskNodeStatus.FAILED: frozenset({TaskNodeStatus.PENDING, TaskNodeStatus.READY, TaskNodeStatus.SKIPPED}),
    TaskNodeStatus.COMPLETE: frozenset(),
    TaskNodeStatus.SKIPPED: frozenset(),
}

LEGACY_MISSION_MAP: dict[str, MissionLifecycle] = {
    "created": MissionLifecycle.QUEUED,
    "planning": MissionLifecycle.PLANNING,
    "active": MissionLifecycle.RUNNING,
    "waiting": MissionLifecycle.BLOCKED,
    "blocked": MissionLifecycle.BLOCKED,
    "escalated": MissionLifecycle.ESCALATED,
    "completed": MissionLifecycle.COMPLETED,
    "failed": MissionLifecycle.FAILED,
    "cancelled": MissionLifecycle.CANCELLED,
}


def migrate_legacy_state(state: MissionLifecycle | str) -> MissionLifecycle:
    if isinstance(state, str):
        try:
            state = MissionLifecycle(state)
        except ValueError:
            mapped = LEGACY_MISSION_MAP.get(state.lower())
            return mapped or MissionLifecycle.QUEUED
    if state.value in LEGACY_MISSION_MAP and state not in MISSION_TRANSITIONS:
        return LEGACY_MISSION_MAP[state.value]
    return state


DISPATCHABLE_MISSION_STATES = frozenset(
    {
        MissionLifecycle.PLANNED,
        MissionLifecycle.DISPATCHED,
        MissionLifecycle.RUNNING,
        MissionLifecycle.RETRYING,
        MissionLifecycle.PLANNING,
        MissionLifecycle.QUEUED,
        MissionLifecycle.ACTIVE,  # legacy
    }
)


TERMINAL_MISSION_STATES = frozenset(
    {
        MissionLifecycle.COMPLETED,
        MissionLifecycle.FAILED,
        MissionLifecycle.CANCELLED,
        MissionLifecycle.ARCHIVED,
    }
)


class TransitionRecord(BaseModel):
    entity: str
    entity_id: str
    from_state: str
    to_state: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str = ""


class MissionStateMachine:
    def __init__(self, mission: Any) -> None:
        self._mission = mission

    @property
    def state(self) -> MissionLifecycle:
        return migrate_legacy_state(self._mission.current_state)

    def transition(self, to_state: MissionLifecycle, *, reason: str = "") -> TransitionRecord:
        from_st = self.state
        to_st = migrate_legacy_state(to_state)
        allowed = MISSION_TRANSITIONS.get(from_st, frozenset())
        if to_st not in allowed and from_st != to_st:
            raise InvalidTransitionError("mission", from_st.value, to_st.value)

        now = datetime.now(timezone.utc)
        self._mission.current_state = to_st
        self._mission.metadata.setdefault("state_entered_at", {})[to_st.value] = now.isoformat()
        self._mission.metadata.setdefault("transition_log", []).append(
            TransitionRecord(
                entity="mission",
                entity_id=self._mission.mission_id,
                from_state=from_st.value,
                to_state=to_st.value,
                timestamp=now,
                reason=reason,
            ).model_dump(mode="json")
        )
        if len(self._mission.metadata["transition_log"]) > 200:
            self._mission.metadata["transition_log"] = self._mission.metadata["transition_log"][-200:]

        logger.info(
            "mission_state_transition",
            mission_id=self._mission.mission_id,
            from_state=from_st.value,
            to_state=to_st.value,
            reason=reason,
        )
        from odin_backend.core.streaming.bridge import get_stream_bridge

        bridge = get_stream_bridge()
        if bridge:
            bridge.mission_state_changed(
                self._mission.mission_id,
                from_state=from_st.value,
                to_state=to_st.value,
                reason=reason,
                trace_id=self._mission.metadata.get("trace_id"),
            )
        return TransitionRecord(
            entity="mission",
            entity_id=self._mission.mission_id,
            from_state=from_st.value,
            to_state=to_st.value,
            reason=reason,
        )

    def duration_in_state(self, state: MissionLifecycle) -> float | None:
        entered = self._mission.metadata.get("state_entered_at", {}).get(state.value)
        if not entered:
            return None
        try:
            ts = datetime.fromisoformat(entered.replace("Z", "+00:00"))
            return (datetime.now(timezone.utc) - ts).total_seconds()
        except ValueError:
            return None


class TaskStateMachine:
    @staticmethod
    def transition(node: Any, to_status: TaskNodeStatus, *, reason: str = "") -> None:
        from_st = node.status
        if from_st == TaskNodeStatus.RUNNING and to_status not in TASK_TRANSITIONS.get(from_st, frozenset()):
            from_st = TaskNodeStatus.EXECUTING
        allowed = TASK_TRANSITIONS.get(from_st, frozenset())
        if to_status not in allowed and from_st != to_status:
            raise InvalidTransitionError("task", from_st.value, to_status.value)
        node.status = to_status
        node.output.setdefault("transition_log", []).append(
            {
                "from": from_st.value,
                "to": to_status.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            }
        )

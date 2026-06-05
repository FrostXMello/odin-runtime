"""Execution timeline builders from causal events and mission state."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.observability.events import TraceEvent
from odin_backend.models.mission import Mission


class TimelineEntry(BaseModel):
    timestamp: str
    kind: str
    source: str
    message: str
    trace_id: str | None = None
    span_id: str | None = None
    agent_id: str | None = None
    task_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    sort_key: float = 0.0


def build_mission_timeline(
    mission: Mission,
    events: list[TraceEvent],
) -> dict[str, Any]:
    entries: list[TimelineEntry] = []

    for e in events:
        entries.append(
            TimelineEntry(
                timestamp=e.timestamp.isoformat(),
                kind=e.kind.value,
                source=e.component,
                message=e.message or e.kind.value,
                trace_id=e.trace_id,
                span_id=e.span_id,
                agent_id=e.agent_id,
                task_id=e.task_id,
                payload=e.payload,
                sort_key=e.timestamp.timestamp(),
            )
        )

    for h in mission.execution_history:
        ts = h.get("timestamp", "")
        entries.append(
            TimelineEntry(
                timestamp=ts,
                kind=h.get("event", "history"),
                source="mission",
                message=h.get("event", ""),
                payload={k: v for k, v in h.items() if k not in ("event", "timestamp")},
                sort_key=_parse_ts(ts),
            )
        )

    for t in mission.metadata.get("transition_log", []):
        entries.append(
            TimelineEntry(
                timestamp=t.get("timestamp", ""),
                kind="state_transition",
                source="lifecycle",
                message=f"{t.get('from_state')} -> {t.get('to_state')}",
                payload=t,
                sort_key=_parse_ts(t.get("timestamp", "")),
            )
        )

    for esc in mission.escalation_events:
        entries.append(
            TimelineEntry(
                timestamp=esc.get("timestamp", ""),
                kind="escalation",
                source="governance",
                message=esc.get("reason", "escalated"),
                task_id=esc.get("task_id"),
                payload=esc,
                sort_key=_parse_ts(esc.get("timestamp", "")),
            )
        )

    for adapt in mission.adaptation_log:
        entries.append(
            TimelineEntry(
                timestamp=adapt.get("timestamp", ""),
                kind="adaptation",
                source="runtime",
                message=adapt.get("action", ""),
                payload=adapt,
                sort_key=_parse_ts(adapt.get("timestamp", "")),
            )
        )

    entries.sort(key=lambda x: x.sort_key)
    return {
        "mission_id": mission.mission_id,
        "trace_id": events[0].trace_id if events else mission.metadata.get("trace_id"),
        "causal_chain_id": events[0].causal_chain_id if events else mission.metadata.get("causal_chain_id"),
        "current_state": mission.current_state.value,
        "entry_count": len(entries),
        "entries": [e.model_dump(mode="json") for e in entries],
    }


def build_task_timeline(
    mission: Mission,
    task_id: str,
    events: list[TraceEvent],
) -> dict[str, Any]:
    node = mission.task_graph.get(task_id)
    entries: list[TimelineEntry] = []

    for e in events:
        entries.append(
            TimelineEntry(
                timestamp=e.timestamp.isoformat(),
                kind=e.kind.value,
                source=e.component,
                message=e.message or e.kind.value,
                trace_id=e.trace_id,
                span_id=e.span_id,
                agent_id=e.agent_id or (node.assigned_agent if node else None),
                task_id=task_id,
                payload=e.payload,
                sort_key=e.timestamp.timestamp(),
            )
        )

    if node:
        for log in node.output.get("transition_log", []):
            entries.append(
                TimelineEntry(
                    timestamp=log.get("timestamp", ""),
                    kind="task_state_transition",
                    source="task_lifecycle",
                    message=f"{log.get('from')} -> {log.get('to')}",
                    payload=log,
                    sort_key=_parse_ts(log.get("timestamp", "")),
                )
            )
        entries.append(
            TimelineEntry(
                timestamp="",
                kind="task_snapshot",
                source="task_graph",
                message=node.goal,
                agent_id=node.assigned_agent,
                task_id=task_id,
                payload={
                    "status": node.status.value,
                    "retry_count": node.retry_count,
                    "tool": node.output.get("tool"),
                },
                sort_key=0.0,
            )
        )

    entries.sort(key=lambda x: x.sort_key)
    return {
        "mission_id": mission.mission_id,
        "task_id": task_id,
        "goal": node.goal if node else None,
        "status": node.status.value if node else "unknown",
        "entry_count": len(entries),
        "entries": [e.model_dump(mode="json") for e in entries],
    }


def _parse_ts(value: str) -> float:
    if not value:
        return 0.0
    try:
        from datetime import datetime

        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0

"""Append-only causal event store with indexes."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from odin_backend.core.observability.events import TraceEvent


class CausalEventStore:
    def __init__(self, *, max_events: int = 50_000) -> None:
        self._events: deque[TraceEvent] = deque(maxlen=max_events)
        self._by_trace: dict[str, list[str]] = defaultdict(list)
        self._by_mission: dict[str, list[str]] = defaultdict(list)
        self._by_task: dict[str, list[str]] = defaultdict(list)
        self._by_chain: dict[str, list[str]] = defaultdict(list)
        self._event_map: dict[str, TraceEvent] = {}

    def append(self, event: TraceEvent) -> TraceEvent:
        self._events.append(event)
        self._event_map[event.event_id] = event
        self._by_trace[event.trace_id].append(event.event_id)
        if event.mission_id:
            self._by_mission[event.mission_id].append(event.event_id)
        if event.task_id:
            self._by_task[event.task_id].append(event.event_id)
        self._by_chain[event.causal_chain_id].append(event.event_id)
        # Trim index lists
        for idx in (self._by_trace, self._by_mission, self._by_task, self._by_chain):
            for key in list(idx.keys()):
                if len(idx[key]) > 2000:
                    idx[key] = idx[key][-1000:]
        return event

    def get_trace_events(self, trace_id: str) -> list[TraceEvent]:
        ids = self._by_trace.get(trace_id, [])
        return sorted(
            [self._event_map[eid] for eid in ids if eid in self._event_map],
            key=lambda e: e.timestamp,
        )

    def get_mission_events(self, mission_id: str) -> list[TraceEvent]:
        ids = self._by_mission.get(mission_id, [])
        return sorted(
            [self._event_map[eid] for eid in ids if eid in self._event_map],
            key=lambda e: e.timestamp,
        )

    def get_task_events(self, task_id: str) -> list[TraceEvent]:
        ids = self._by_task.get(task_id, [])
        return sorted(
            [self._event_map[eid] for eid in ids if eid in self._event_map],
            key=lambda e: e.timestamp,
        )

    def get_chain_events(self, causal_chain_id: str) -> list[TraceEvent]:
        ids = self._by_chain.get(causal_chain_id, [])
        return sorted(
            [self._event_map[eid] for eid in ids if eid in self._event_map],
            key=lambda e: e.timestamp,
        )

    def recent(self, limit: int = 100) -> list[TraceEvent]:
        return list(self._events)[-limit:]

    def stats(self) -> dict[str, Any]:
        return {
            "total_events": len(self._events),
            "traces": len(self._by_trace),
            "missions": len(self._by_mission),
            "tasks": len(self._by_task),
            "chains": len(self._by_chain),
        }

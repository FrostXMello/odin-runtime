"""Mission scheduler — deferred execution and retry queues."""

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ScheduledMissionTick:
    mission_id: str
    run_at: float
    reason: str = "scheduled"


class MissionScheduler:
    def __init__(self, *, cooldown_seconds: float = 2.0) -> None:
        self._queue: deque[ScheduledMissionTick] = deque()
        self._retry_queue: deque[ScheduledMissionTick] = deque()
        self._cooldown = cooldown_seconds
        self._last_tick: dict[str, float] = {}
        self._queued_ids: set[str] = set()

    def schedule(self, mission_id: str, *, delay_seconds: float = 0.0, reason: str = "scheduled") -> None:
        if mission_id in self._queued_ids:
            return
        self._queued_ids.add(mission_id)
        self._queue.append(
            ScheduledMissionTick(
                mission_id=mission_id,
                run_at=time.monotonic() + delay_seconds,
                reason=reason,
            )
        )

    def schedule_retry(self, mission_id: str, *, delay_seconds: float | None = None) -> None:
        if mission_id in self._queued_ids:
            return
        delay = delay_seconds if delay_seconds is not None else self._cooldown
        self._queued_ids.add(mission_id)
        self._retry_queue.append(
            ScheduledMissionTick(
                mission_id=mission_id,
                run_at=time.monotonic() + delay,
                reason="retry",
            )
        )

    def pop_due(self) -> list[str]:
        now = time.monotonic()
        due: list[str] = []
        while self._queue and self._queue[0].run_at <= now:
            tick = self._queue.popleft()
            self._queued_ids.discard(tick.mission_id)
            if self._cooldown_elapsed(tick.mission_id, now):
                due.append(tick.mission_id)
                self._last_tick[tick.mission_id] = now
        while self._retry_queue and self._retry_queue[0].run_at <= now:
            tick = self._retry_queue.popleft()
            self._queued_ids.discard(tick.mission_id)
            if self._cooldown_elapsed(tick.mission_id, now):
                due.append(tick.mission_id)
                self._last_tick[tick.mission_id] = now
        return due

    def _cooldown_elapsed(self, mission_id: str, now: float) -> bool:
        last = self._last_tick.get(mission_id, 0.0)
        return now - last >= self._cooldown

    def backlog_depth(self) -> int:
        return len(self._queue) + len(self._retry_queue)

    def peek_due_ids(self) -> list[str]:
        """Non-destructive view of missions that would run now."""
        import time as _time

        now = _time.monotonic()
        due: list[str] = []
        for tick in self._queue:
            if tick.run_at <= now and self._cooldown_elapsed(tick.mission_id, now):
                due.append(tick.mission_id)
        for tick in self._retry_queue:
            if tick.run_at <= now and self._cooldown_elapsed(tick.mission_id, now):
                if tick.mission_id not in due:
                    due.append(tick.mission_id)
        return due[:20]

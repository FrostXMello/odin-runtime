"""Mission garbage collection and retention."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from odin_backend.core.missions.lifecycle import migrate_legacy_state, TERMINAL_MISSION_STATES
from odin_backend.models.mission import Mission, MissionLifecycle
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class MissionGarbageCollector:
    def __init__(
        self,
        store: Any,
        *,
        stale_seconds: int = 7200,
        retention_limit: int = 500,
    ) -> None:
        self._store = store
        self._stale_seconds = stale_seconds
        self._retention_limit = retention_limit
        self._last_run: datetime | None = None
        self._stats: dict[str, int] = {
            "archived": 0,
            "expired": 0,
            "cancelled_stale": 0,
            "orphans_removed": 0,
        }

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    async def run(self, manager: Any) -> dict[str, int]:
        now = datetime.now(timezone.utc)
        missions = await self._store.list_all(limit=self._retention_limit * 2)
        active_non_terminal = 0

        for mission in missions:
            state = migrate_legacy_state(mission.current_state)
            if state in TERMINAL_MISSION_STATES:
                if state != MissionLifecycle.ARCHIVED:
                    await self._archive(mission, manager)
                continue

            active_non_terminal += 1
            age = (now - mission.updated_at.replace(tzinfo=timezone.utc)).total_seconds()
            if age > self._stale_seconds:
                await self._expire_stale(mission, manager, age=age)

        self._prune_orphan_tasks(missions)
        self._last_run = now
        logger.info("mission_gc_completed", **self._stats, active_non_terminal=active_non_terminal)
        return self._stats

    async def _archive(self, mission: Mission, manager: Any) -> None:
        from odin_backend.core.missions.lifecycle import MissionStateMachine

        sm = MissionStateMachine(mission)
        try:
            if migrate_legacy_state(mission.current_state) != MissionLifecycle.ARCHIVED:
                sm.transition(MissionLifecycle.ARCHIVED, reason="gc_archive")
        except Exception:
            mission.current_state = MissionLifecycle.ARCHIVED
        await manager.persist(mission)
        manager._active.pop(mission.mission_id, None)
        self._stats["archived"] += 1

    async def _expire_stale(self, mission: Mission, manager: Any, *, age: float) -> None:
        from odin_backend.core.missions.lifecycle import MissionStateMachine

        sm = MissionStateMachine(mission)
        try:
            sm.transition(MissionLifecycle.CANCELLED, reason="stale_timeout")
        except Exception:
            mission.current_state = MissionLifecycle.CANCELLED
        mission.append_history("expired_stale", {"age_seconds": age})
        await manager.persist(mission)
        manager._active.pop(mission.mission_id, None)
        self._stats["expired"] += 1
        logger.warning("mission_expired_stale", mission_id=mission.mission_id, age_seconds=age)

    def _prune_orphan_tasks(self, missions: list[Mission]) -> None:
        for mission in missions:
            valid_ids = set(mission.task_graph.nodes.keys())
            for node in list(mission.task_graph.nodes.values()):
                node.dependencies = [d for d in node.dependencies if d in valid_ids]
            removed = 0
            for ref_list in (mission.active_tasks, mission.completed_tasks, mission.blocked_tasks):
                before = len(ref_list)
                ref_list[:] = [r for r in ref_list if r.task_id in valid_ids]
                removed += before - len(ref_list)
            if removed:
                self._stats["orphans_removed"] += removed

"""Mission manager — lifecycle CRUD, deduplication, and persistence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from odin_backend.core.missions.dedup import build_fingerprint, MissionDeduplicator
from odin_backend.core.missions.lifecycle import (
    DISPATCHABLE_MISSION_STATES,
    migrate_legacy_state,
    MissionStateMachine,
    TERMINAL_MISSION_STATES,
)
from odin_backend.core.missions.planner import MissionPlanner
from odin_backend.core.missions.policy import ExecutionPolicyEnforcer
from odin_backend.core.missions.state_store import MissionStateStore
from odin_backend.models.mission import Mission, MissionLifecycle
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class MissionDuplicateError(Exception):
    def __init__(self, message: str, *, duplicate_mission_id: str | None = None, action: str = "") -> None:
        super().__init__(message)
        self.duplicate_mission_id = duplicate_mission_id
        self.action = action


@dataclass
class MissionCreateResult:
    mission: Mission
    created: bool = True
    duplicate_of: str | None = None
    suppressed: bool = False


class MissionManager:
    def __init__(
        self,
        store: MissionStateStore,
        planner: MissionPlanner,
        *,
        memory_index: Any | None = None,
        deduplicator: MissionDeduplicator | None = None,
        policy: ExecutionPolicyEnforcer | None = None,
        replay_window_seconds: int = 3600,
        observability: Any | None = None,
    ) -> None:
        self._store = store
        self._planner = planner
        self._memory_index = memory_index
        self.deduplicator = deduplicator or MissionDeduplicator(replay_window_seconds=replay_window_seconds)
        self.policy = policy or ExecutionPolicyEnforcer()
        self._obs = observability
        self._active: dict[str, Mission] = {}

    async def connect(self) -> None:
        await self._store.connect()

    async def restore_active(self, *, max_restore: int = 20) -> list[Mission]:
        missions = await self._store.list_active()
        restored: list[Mission] = []
        for m in missions[:max_restore]:
            m.current_state = migrate_legacy_state(m.current_state)
            self._active[m.mission_id] = m
            restored.append(m)
        if len(missions) > max_restore:
            logger.warning(
                "mission_restore_capped",
                total=len(missions),
                restored=max_restore,
            )
        logger.info("missions_restored", count=len(restored))
        return restored

    async def create(
        self,
        objective: str,
        *,
        priority: int = 50,
        autonomy_level: int = 1,
        created_by: str = "user",
        human_approved: bool = False,
        plan_immediately: bool = True,
        mission_type: str = "standard",
        originating_signal: str = "api",
        planning_context: str = "",
        allow_duplicate: bool = False,
    ) -> Mission:
        result = await self.create_checked(
            objective,
            priority=priority,
            autonomy_level=autonomy_level,
            created_by=created_by,
            human_approved=human_approved,
            plan_immediately=plan_immediately,
            mission_type=mission_type,
            originating_signal=originating_signal,
            planning_context=planning_context,
        )
        if result.suppressed and result.duplicate_of and not allow_duplicate:
            raise MissionDuplicateError(
                "duplicate mission blocked",
                duplicate_mission_id=result.duplicate_of,
                action="duplicate_active",
            )
        return result.mission

    async def create_checked(
        self,
        objective: str,
        *,
        priority: int = 50,
        autonomy_level: int = 1,
        created_by: str = "user",
        human_approved: bool = False,
        plan_immediately: bool = True,
        mission_type: str = "standard",
        originating_signal: str = "api",
        planning_context: str = "",
    ) -> MissionCreateResult:
        fingerprint = build_fingerprint(
            objective,
            mission_type=mission_type,
            originating_signal=originating_signal,
            planning_context=planning_context,
        )

        existing = await self._store.list_all(limit=200)
        dedup = self.deduplicator.evaluate(fingerprint, existing)
        if not dedup.allow and dedup.duplicate_mission_id:
            self.deduplicator.record_suppressed()
            if self._obs:
                from odin_backend.core.observability.events import TraceEventKind

                self._obs.tracer.record(
                    TraceEventKind.DUPLICATE_SUPPRESSED,
                    message="duplicate mission suppressed",
                    payload={"duplicate_of": dedup.duplicate_mission_id, "action": dedup.action},
                    component="deduplicator",
                )
            existing_mission = await self.get(dedup.duplicate_mission_id)
            if existing_mission:
                return MissionCreateResult(
                    mission=existing_mission,
                    created=False,
                    duplicate_of=dedup.duplicate_mission_id,
                    suppressed=True,
                )

        assessment = self.policy.assess_objective(objective, human_approved=human_approved)
        if assessment.verdict.value == "deny":
            raise MissionDuplicateError(f"policy denied: {assessment.reasons}")

        mission = Mission(
            objective=objective,
            priority=priority,
            autonomy_level=autonomy_level,
            created_by=created_by,
            human_approved=human_approved or assessment.requires_human_approval,
            current_state=MissionLifecycle.QUEUED,
        )
        mission.metadata["fingerprint_digest"] = fingerprint.digest
        mission.metadata["fingerprint"] = fingerprint.to_dict()
        mission.metadata["policy_assessment"] = assessment.model_dump()
        if assessment.sandbox_only:
            mission.execution_strategy = "sandbox_only"

        sm = MissionStateMachine(mission)
        sm.transition(MissionLifecycle.QUEUED, reason="created")
        mission.append_history("created", {"created_by": created_by, "digest": fingerprint.digest})

        if assessment.requires_human_approval and not human_approved:
            sm.transition(MissionLifecycle.APPROVAL_REQUIRED, reason="policy")
            if self._obs:
                from odin_backend.core.observability.events import TraceEventKind

                ctx = self._obs.tracer.start_mission_trace(mission.mission_id, objective=objective)
                mission.metadata["trace_id"] = ctx.trace_id
                mission.metadata["causal_chain_id"] = ctx.causal_chain_id
                self._obs.tracer.record(
                    TraceEventKind.POLICY_BLOCKED,
                    message="approval required",
                    payload={"rules": assessment.matched_rules},
                    component="policy",
                )
            await self.persist(mission)
            self._active[mission.mission_id] = mission
            return MissionCreateResult(mission=mission, created=True)

        if plan_immediately:
            sm.transition(MissionLifecycle.PLANNING, reason="auto_plan")
            self._planner.plan(mission)
            sm.transition(MissionLifecycle.PLANNED, reason="planned")

        if self._obs:
            from odin_backend.core.observability.events import TraceEventKind

            ctx = self._obs.tracer.start_mission_trace(mission.mission_id, objective=objective)
            mission.metadata["trace_id"] = ctx.trace_id
            mission.metadata["causal_chain_id"] = ctx.causal_chain_id
            self._obs.tracer.record(
                TraceEventKind.MISSION_CREATED,
                message="mission persisted",
                payload={"created_by": created_by, "state": mission.current_state.value},
                component="mission_manager",
            )

        if self._memory_index:
            mem_id = await self._memory_index.link_mission_start(mission.mission_id, objective)
            mission.memory_refs.append(mem_id)

        self._active[mission.mission_id] = mission
        await self.persist(mission)
        return MissionCreateResult(mission=mission, created=True)

    async def get(self, mission_id: str) -> Mission | None:
        if mission_id in self._active:
            return self._active[mission_id]
        mission = await self._store.get(mission_id)
        if mission:
            mission.current_state = migrate_legacy_state(mission.current_state)
            self._active[mission_id] = mission
        return mission

    async def list_missions(self, *, limit: int = 100) -> list[Mission]:
        return await self._store.list_all(limit=limit)

    async def list_active_missions(self) -> list[Mission]:
        return await self._store.list_active()

    async def persist(self, mission: Mission) -> None:
        mission.touch()
        mission.sync_task_lists()
        await self._store.save(mission)
        if not mission.is_terminal():
            self._active[mission.mission_id] = mission
        else:
            self._active.pop(mission.mission_id, None)

    async def pause(self, mission_id: str, *, reason: str = "user_pause") -> Mission | None:
        mission = await self.get(mission_id)
        if not mission or mission.is_terminal():
            return mission
        sm = MissionStateMachine(mission)
        sm.transition(MissionLifecycle.BLOCKED, reason=reason)
        mission.pause_reason = reason
        mission.append_history("paused", {"reason": reason})
        await self.persist(mission)
        return mission

    async def resume(self, mission_id: str) -> Mission | None:
        mission = await self.get(mission_id)
        if not mission or mission.is_terminal():
            return mission
        if migrate_legacy_state(mission.current_state) == MissionLifecycle.APPROVAL_REQUIRED:
            if not mission.human_approved:
                return mission
        sm = MissionStateMachine(mission)
        sm.transition(MissionLifecycle.RUNNING, reason="resumed")
        mission.pause_reason = None
        mission.append_history("resumed")
        await self.persist(mission)
        return mission

    async def cancel(self, mission_id: str, *, reason: str = "user_cancel") -> Mission | None:
        mission = await self.get(mission_id)
        if not mission or mission.is_terminal():
            return mission
        sm = MissionStateMachine(mission)
        sm.transition(MissionLifecycle.CANCELLED, reason=reason)
        mission.append_history("cancelled", {"reason": reason})
        await self.persist(mission)
        return mission

    async def approve(self, mission_id: str) -> Mission | None:
        mission = await self.get(mission_id)
        if not mission:
            return None
        mission.human_approved = True
        sm = MissionStateMachine(mission)
        if sm.state == MissionLifecycle.APPROVAL_REQUIRED:
            if not mission.task_graph.nodes:
                self._planner.plan(mission)
            sm.transition(MissionLifecycle.PLANNED, reason="human_approved")
        if sm.state in (MissionLifecycle.ESCALATED, MissionLifecycle.BLOCKED):
            sm.transition(MissionLifecycle.RUNNING, reason="human_approved")
        mission.append_history("human_approved")
        await self.persist(mission)
        return mission

    def active_count(self) -> int:
        return sum(
            1
            for m in self._active.values()
            if migrate_legacy_state(m.current_state) not in TERMINAL_MISSION_STATES
        )

    def dispatchable_count(self) -> int:
        return sum(
            1
            for m in self._active.values()
            if migrate_legacy_state(m.current_state) in DISPATCHABLE_MISSION_STATES
        )

    def diagnostics(self) -> dict[str, Any]:
        return {
            "active_missions": self.active_count(),
            "dispatchable_missions": self.dispatchable_count(),
            "cached": len(self._active),
            **self.deduplicator.metrics,
            "policy_violations": self.policy.violation_count,
        }

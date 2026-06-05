"""Adaptive runtime — retry vs replan vs escalate with confidence awareness."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from odin_backend.core.execution.models import ExecutionState
from odin_backend.core.planning.confidence import PlannerConfidenceProfile, confidence_action
from odin_backend.models.mission import Mission
from odin_backend.models.task_graph import TaskNode, TaskNodeStatus


@dataclass
class AdaptiveDecision:
    action: str  # retry | replan | escalate | continue | isolate_branch
    reason: str
    payload: dict[str, Any] = field(default_factory=dict)


def _mission_plan_confidence(mission: Mission) -> float:
    conf = mission.confidence
    if isinstance(conf, dict):
        profile = PlannerConfidenceProfile(
            plan=float(conf.get("plan", 0.75)),
            task=float(conf.get("task", 0.75)),
            tool=float(conf.get("tool", 0.75)),
            dependency=float(conf.get("dependency", 0.8)),
            recovery=float(conf.get("recovery", 0.7)),
        )
        return profile.aggregate
    if isinstance(conf, (int, float)):
        return float(conf)
    return 0.75


class AdaptiveRuntimeCoordinator:
    """Observes execution failures and recommends mission-level responses."""

    def __init__(self) -> None:
        self._mission_state: dict[str, dict[str, Any]] = {}

    def snapshot(self, app: Any) -> dict[str, Any]:
        missions = {}
        for mid in list(getattr(app.mission_manager, "_active", {}).keys())[:20]:  # noqa: SLF001
            missions[mid] = self._mission_state.get(mid, {})
        return {
            "missions": missions,
            "adaptive_policy": app.adaptive_policy.state.model_dump()
            if hasattr(app, "adaptive_policy")
            else {},
            "async_runtime": getattr(app, "async_mission_runtime", None).metrics
            if hasattr(app, "async_mission_runtime")
            else {},
            "dispatcher": app.mission_dispatcher.metrics
            if hasattr(app, "mission_dispatcher")
            else {},
        }

    def record_outcome(
        self,
        mission_id: str,
        *,
        task_id: str,
        success: bool,
        execution_state: str,
    ) -> None:
        st = self._mission_state.setdefault(mission_id, {"failures": 0, "timeouts": 0, "tasks": {}})
        st["tasks"][task_id] = {"success": success, "state": execution_state}
        if not success:
            st["failures"] = st.get("failures", 0) + 1
        if execution_state == ExecutionState.TIMED_OUT.value:
            st["timeouts"] = st.get("timeouts", 0) + 1

    def decide(
        self,
        app: Any,
        mission: Mission,
        task: TaskNode,
        *,
        execution_state: str,
        contract_blocking: bool,
    ) -> AdaptiveDecision:
        self.record_outcome(
            mission.mission_id,
            task_id=task.id,
            success=execution_state == ExecutionState.COMPLETED.value,
            execution_state=execution_state,
        )
        st = self._mission_state.get(mission.mission_id, {})
        failures = st.get("failures", 0)
        plan_conf = _mission_plan_confidence(mission)
        conf_actions = (mission.metadata.get("semantic_plan") or {}).get("confidence_actions") or {}

        if execution_state == ExecutionState.COMPLETED.value:
            return AdaptiveDecision(action="continue", reason="execution_ok")

        if execution_state == ExecutionState.CANCELLED.value:
            return AdaptiveDecision(action="continue", reason="cancelled")

        if plan_conf < 0.35 and failures >= 2:
            return AdaptiveDecision(
                action="escalate",
                reason="low_plan_confidence_failures",
                payload={"plan_confidence": plan_conf, "task_id": task.id},
            )

        if task.retry_count >= mission.max_retries:
            if contract_blocking:
                return AdaptiveDecision(
                    action="escalate",
                    reason="blocking_task_max_retries",
                    payload={"task_id": task.id},
                )
            return AdaptiveDecision(
                action="isolate_branch",
                reason="non_blocking_failure",
                payload={"task_id": task.id},
            )

        if failures >= 3:
            if plan_conf < 0.45:
                return AdaptiveDecision(
                    action="replan",
                    reason="low_confidence_failures",
                    payload={"plan_confidence": plan_conf},
                )
            if hasattr(app, "confidence"):
                snap = app.confidence.for_mission(mission.mission_id)
                if snap.aggregate < 0.35:
                    return AdaptiveDecision(action="replan", reason="low_confidence_failures")

        if st.get("timeouts", 0) >= 2:
            return AdaptiveDecision(action="replan", reason="execution_timeouts")

        if plan_conf < 0.5 and conf_actions.get("validation_checkpoints", 0) >= 2:
            return AdaptiveDecision(
                action="retry",
                reason="low_confidence_validation_retry",
                payload={"task_id": task.id, "delay_multiplier": 1.5},
            )

        if execution_state in (ExecutionState.FAILED.value, ExecutionState.TIMED_OUT.value):
            return AdaptiveDecision(action="retry", reason="execution_failed", payload={"task_id": task.id})

        return AdaptiveDecision(action="retry", reason="unknown_failure")

    async def apply_decision(
        self,
        app: Any,
        mission: Mission,
        task: TaskNode,
        decision: AdaptiveDecision,
        *,
        runtime: Any,
    ) -> dict[str, Any]:
        from odin_backend.core.missions.lifecycle import MissionStateMachine
        from odin_backend.core.observability.events import TraceEventKind
        from odin_backend.models.mission import MissionLifecycle

        sm = MissionStateMachine(mission)
        obs = getattr(app, "observability", None)

        if decision.action == "continue":
            return {"applied": False}

        if decision.action == "retry":
            mission.task_graph.update_status(task.id, TaskNodeStatus.PENDING, reason="execution_retry")
            task.retry_count += 1
            if obs:
                obs.tracer.record(
                    TraceEventKind.RETRY_TRIGGERED,
                    message=decision.reason,
                    payload={"task_id": task.id, "source": "adaptive_runtime"},
                    component="adaptive_runtime",
                )
            fail_intel = getattr(app, "failure_intelligence", None)
            if fail_intel:
                fail_intel.record_adaptation(mission.mission_id, "retry")
            return {"applied": True, "action": "retry"}

        if decision.action == "replan":
            runtime._planner.replan(mission, reason=decision.reason)  # noqa: SLF001
            mission.append_adaptation("replan", reason=decision.reason)
            fail_intel = getattr(app, "failure_intelligence", None)
            if fail_intel:
                fail_intel.record_adaptation(mission.mission_id, "replan")
            if sm.state == MissionLifecycle.RUNNING:
                sm.transition(MissionLifecycle.RETRYING, reason=decision.reason)
                sm.transition(MissionLifecycle.RUNNING, reason="adaptive_replan_resume")
            if obs:
                obs.tracer.record(
                    TraceEventKind.REPLAN_GENERATED,
                    message=f"adaptive_replan: {decision.reason}",
                    payload={"mission_id": mission.mission_id},
                    component="adaptive_runtime",
                )
            return {"applied": True, "action": "replan"}

        if decision.action == "escalate":
            sm.transition(MissionLifecycle.ESCALATED, reason=decision.reason)
            if obs:
                obs.tracer.record(
                    TraceEventKind.ESCALATION_TRIGGERED,
                    message=decision.reason,
                    component="adaptive_runtime",
                )
            return {"applied": True, "action": "escalate"}

        if decision.action == "isolate_branch":
            mission.task_graph.update_status(task.id, TaskNodeStatus.SKIPPED, reason=decision.reason, strict=False)
            return {"applied": True, "action": "isolate_branch"}

        return {"applied": False}

    async def apply_decision_async(
        self,
        app: Any,
        mission: Mission,
        task: TaskNode,
        decision: AdaptiveDecision,
        *,
        runtime: Any,
    ) -> dict[str, Any]:
        backoff = getattr(app.settings, "execution_retry_backoff_seconds", 2.0)
        if decision.action == "retry":
            result = await self.apply_decision(app, mission, task, decision, runtime=runtime)
            if result.get("applied"):
                mult = decision.payload.get("delay_multiplier", 1.0)
                result["delay"] = backoff * max(1, task.retry_count) * mult
            return result
        return await self.apply_decision(app, mission, task, decision, runtime=runtime)

"""Mission runtime — adaptive wave execution with perception feedback."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from odin_backend.core.checkpoints.mission_checkpoint import MissionCheckpointEngine
from odin_backend.core.missions.governance import MissionGovernance
from odin_backend.core.missions.lifecycle import (
    MissionStateMachine,
    TaskStateMachine,
    migrate_legacy_state,
)
from odin_backend.core.missions.planner import MissionPlanner
from odin_backend.core.missions.policy import ExecutionPolicyEnforcer
from odin_backend.models.mission import Mission, MissionLifecycle
from odin_backend.models.task_graph import TaskNode, TaskNodeStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class MissionRuntime:
    """
    Executes cognition waves with adaptive replanning, feedback, and confidence.
    """

    def __init__(
        self,
        planner: MissionPlanner,
        governance: MissionGovernance,
        checkpoints: MissionCheckpointEngine,
        memory_index: Any,
        *,
        feedback: Any | None = None,
        confidence: Any | None = None,
        policy: ExecutionPolicyEnforcer | None = None,
    ) -> None:
        self._planner = planner
        self._governance = governance
        self._checkpoints = checkpoints
        self._memory = memory_index
        self._feedback = feedback
        self._confidence = confidence
        self._policy = policy or ExecutionPolicyEnforcer()
        self._metrics: dict[str, int] = {
            "waves_executed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "retries": 0,
            "escalations": 0,
            "adaptations": 0,
            "recoveries": 0,
        }

    @property
    def metrics(self) -> dict[str, Any]:
        out = dict(self._metrics)
        if self._metrics["tasks_completed"] + self._metrics["tasks_failed"] > 0:
            out["execution_recovery_rate"] = round(
                self._metrics["recoveries"] / max(1, self._metrics["tasks_failed"]),
                3,
            )
        else:
            out["execution_recovery_rate"] = 1.0
        return out

    async def run_wave(self, app: Any, mission: Mission) -> dict[str, Any]:
        if mission.is_terminal():
            return {"skipped": True, "state": mission.current_state.value}

        sm = MissionStateMachine(mission)
        state = sm.state

        if state == MissionLifecycle.APPROVAL_REQUIRED:
            return {"skipped": True, "state": "approval_required"}

        if state == MissionLifecycle.ESCALATED:
            return {"skipped": True, "state": "escalated", "reason": "awaiting_human"}

        if state in (MissionLifecycle.QUEUED, MissionLifecycle.CREATED):
            sm.transition(MissionLifecycle.PLANNING, reason="wave")
            self._planner.plan(mission)
            sm.transition(MissionLifecycle.PLANNED, reason="wave_planned")

        if sm.state == MissionLifecycle.PLANNING:
            self._planner.plan(mission)
            sm.transition(MissionLifecycle.PLANNED, reason="wave_planned")

        if sm.state == MissionLifecycle.PLANNED:
            sm.transition(MissionLifecycle.DISPATCHED, reason="wave")
        if sm.state == MissionLifecycle.DISPATCHED:
            sm.transition(MissionLifecycle.RUNNING, reason="wave")

        policy_check = self._policy.assess_objective(
            mission.objective, human_approved=mission.human_approved
        )
        if policy_check.requires_human_approval and not mission.human_approved:
            sm.transition(MissionLifecycle.APPROVAL_REQUIRED, reason="policy_runtime")
            await app.mission_manager.persist(mission)
            return {"skipped": True, "state": "approval_required", "policy": True}

        self._apply_adaptive_policy(app, mission)

        ready = mission.task_graph.ready_nodes()
        if not ready:
            return await self._evaluate_completion(app, mission)

        max_tasks = app.settings.mission_max_concurrent_tasks
        if hasattr(app, "adaptive_policy"):
            max_tasks = min(max_tasks, app.adaptive_policy.state.concurrency_limit)

        async_mode = getattr(app.settings, "async_mission_runtime_enabled", True) and hasattr(
            app, "async_mission_runtime"
        )
        results: list[dict[str, Any]] = []
        submitted_async = 0

        for task in ready[:max_tasks]:
            self._begin_task(app, mission, task)
            allowed, profile, reason = await self._governance.validate_execution(
                app, mission, task
            )
            if not allowed:
                obs = getattr(app, "observability", None)
                if profile.requires_confirmation:
                    if obs:
                        from odin_backend.core.observability.events import TraceEventKind

                        obs.tracer.record(
                            TraceEventKind.ESCALATION_TRIGGERED,
                            message=reason,
                            payload={"task_id": task.id},
                            component="governance",
                        )
                        obs.metrics.record_escalation(mission_id=mission.mission_id)
                    sm.transition(MissionLifecycle.ESCALATED, reason="governance")
                    mission.escalation_events.append(
                        {"task_id": task.id, "reason": reason, "profile": profile.model_dump()}
                    )
                    self._metrics["escalations"] += 1
                    mission.task_graph.update_status(
                        task.id, TaskNodeStatus.BLOCKED, reason="governance_escalation"
                    )
                    mission.append_history("escalated", {"task_id": task.id, "reason": reason})
                    await self._post_feedback(app, mission, task, False, reason)
                    continue

                mission.task_graph.update_status(task.id, TaskNodeStatus.FAILED, reason="governance_deny")
                self._metrics["tasks_failed"] += 1
                results.append({"task_id": task.id, "success": False, "reason": reason})
                await self._post_feedback(app, mission, task, False, reason)
                continue

            if async_mode:
                sub = await app.async_mission_runtime.submit_from_wave(
                    app, mission, task, runtime=self
                )
                results.append(sub)
                if sub.get("async"):
                    submitted_async += 1
                elif sub.get("inline") and sub.get("success"):
                    mission.task_graph.update_status(
                        task.id, TaskNodeStatus.COMPLETE, reason="inline_complete"
                    )
                continue

            success = await self._execute_task(app, mission, task)
            await self._post_feedback(app, mission, task, success, "" if success else "execution_failed")

            obs = getattr(app, "observability", None)
            if success:
                mission.task_graph.update_status(
                    task.id,
                    TaskNodeStatus.COMPLETE,
                    output={"completed": True},
                    reason="execution_success",
                )
                self._metrics["tasks_completed"] += 1
                if obs:
                    from odin_backend.core.observability.events import TraceEventKind

                    obs.tracer.record(
                        TraceEventKind.TASK_COMPLETED,
                        message=task.goal[:80],
                        payload={"tool": task.output.get("tool", "noop")},
                        component="mission_runtime",
                    )
                await self._memory.link_task_completion(mission.mission_id, task.id, task.goal)
            else:
                if obs:
                    from odin_backend.core.observability.events import TraceEventKind

                    obs.tracer.record(
                        TraceEventKind.TASK_FAILED,
                        message=task.goal[:80],
                        component="mission_runtime",
                    )
                adapted = await self._handle_task_failure(app, mission, task)
                if adapted.get("recovered"):
                    self._metrics["recoveries"] += 1
                results.append({"task_id": task.id, "success": adapted.get("success", False)})

        mission.current_wave += 1
        self._metrics["waves_executed"] += 1
        mission.sync_task_lists()

        if async_mode and submitted_async:
            obs = getattr(app, "observability", None)
            if obs:
                from odin_backend.core.observability.events import TraceEventKind

                obs.tracer.record(
                    TraceEventKind.ASYNC_WAVE_DISPATCHED,
                    message=f"submitted {submitted_async} tasks",
                    payload={"submitted": submitted_async, "in_flight": app.async_mission_runtime.in_flight_count(mission.mission_id)},
                    component="mission_runtime",
                )
            app.async_mission_runtime._metrics["async_waves_dispatched"] += 1
            await app.mission_manager.persist(mission)
            return {
                "state": migrate_legacy_state(mission.current_state).value,
                "async": True,
                "submitted": submitted_async,
                "in_flight": app.async_mission_runtime.in_flight_count(mission.mission_id),
                "wave_results": results,
            }

        force_ckpt = (
            hasattr(app, "adaptive_policy")
            and app.adaptive_policy.state.checkpoint_interval <= 1
        )
        if force_ckpt or mission.current_wave % 1 == 0:
            ckpt = self._checkpoints.create_checkpoint(
                mission, label=f"wave_{mission.current_wave}"
            )
            await self._checkpoints.persist(mission, ckpt)

        return await self._evaluate_completion(app, mission, wave_results=results)

    def _begin_task(self, app: Any, mission: Mission, task: TaskNode) -> None:
        obs = getattr(app, "observability", None)
        if obs:
            from odin_backend.core.observability.events import TraceEventKind

            obs.tracer.link_task(mission.mission_id, task.id)
            obs.tracer.record(
                TraceEventKind.TASK_ASSIGNED,
                message=task.goal[:80],
                payload={"agent": task.assigned_agent},
                component="mission_runtime",
            )
        st = task.status
        if st == TaskNodeStatus.READY:
            TaskStateMachine.transition(task, TaskNodeStatus.ASSIGNED, reason="dispatch")
        if task.status == TaskNodeStatus.ASSIGNED:
            TaskStateMachine.transition(task, TaskNodeStatus.EXECUTING, reason="dispatch")
        elif task.status == TaskNodeStatus.RUNNING:
            pass
        elif task.status == TaskNodeStatus.PENDING:
            TaskStateMachine.transition(task, TaskNodeStatus.READY, reason="dispatch")
            TaskStateMachine.transition(task, TaskNodeStatus.ASSIGNED, reason="dispatch")
            TaskStateMachine.transition(task, TaskNodeStatus.EXECUTING, reason="dispatch")
        task.output["executing_started_at"] = datetime.now(timezone.utc).isoformat()
        if obs:
            from odin_backend.core.observability.events import TraceEventKind

            obs.tracer.record(
                TraceEventKind.TASK_STARTED,
                message=task.goal[:80],
                payload={"tool": task.output.get("tool", "noop")},
                component="mission_runtime",
            )

    def _apply_adaptive_policy(self, app: Any, mission: Mission) -> None:
        if not hasattr(app, "adaptive_policy") or not self._confidence:
            return
        snap = self._confidence.for_mission(mission.mission_id)
        app.adaptive_policy.apply_instability(
            confidence=snap,
            failure_count=self._metrics["tasks_failed"],
            repeated_tool_failures=snap.tool_reliability < 0.4,
        )

    async def _post_feedback(
        self,
        app: Any,
        mission: Mission,
        task: TaskNode,
        success: bool,
        reason: str,
    ) -> None:
        tool = task.output.get("tool", "noop")
        if self._feedback:
            report = self._feedback.process(
                success=success,
                tool=tool,
                reason=reason,
                mission_id=mission.mission_id,
                task_id=task.id,
            )
            for p in report.perceptions:
                await app.perception.ingest(p)
            if self._confidence:
                snap = self._confidence.for_mission(mission.mission_id)
                if report.confidence_decay:
                    snap = snap.decay(**report.confidence_decay)
                elif success:
                    snap = snap.reinforce(execution=0.02, stability=0.02)
                self._confidence.set_mission(mission.mission_id, snap)
                mission.confidence = {
                    "execution": snap.execution_confidence,
                    "environment": snap.environmental_certainty,
                    "stability": snap.mission_stability,
                }
                self._confidence.record_tool_outcome(tool, success)
            if not success:
                await self._apply_adaptation(app, mission, report)

        if hasattr(app, "perception"):
            await app.perception.ingest_execution(
                tool=tool,
                success=success,
                mission_id=mission.mission_id,
                task_id=task.id,
            )

    async def _apply_adaptation(self, app: Any, mission: Mission, report: Any) -> None:
        sm = MissionStateMachine(mission)
        for action in report.recommended_actions:
            mission.append_adaptation(action.action, reason=action.reason, detail=action.payload)
            self._metrics["adaptations"] += 1

            if action.action == "switch_strategy":
                mission.execution_strategy = "conservative_readonly"
                for node in mission.task_graph.nodes.values():
                    if node.status == TaskNodeStatus.PENDING:
                        node.output["tool"] = "noop"
                app.perception_memory.record_strategy(
                    mission.mission_id, mission.execution_strategy, reason=action.reason
                )

            elif action.action == "replan" or report.should_replan:
                self._planner.replan(mission, reason=action.reason)
                self._metrics["recoveries"] += 1
                if sm.state == MissionLifecycle.RUNNING:
                    sm.transition(MissionLifecycle.RETRYING, reason="replan")
                    sm.transition(MissionLifecycle.RUNNING, reason="replan_resume")

            elif action.action == "escalate":
                sm.transition(MissionLifecycle.ESCALATED, reason=action.reason)

            elif action.action == "reduce_concurrency" and hasattr(app, "adaptive_policy"):
                app.adaptive_policy.apply_instability(
                    confidence=self._confidence.for_mission(mission.mission_id),
                    failure_count=self._metrics["tasks_failed"] + 1,
                    repeated_tool_failures=True,
                )

        if report.should_rollback:
            await app.mission_checkpoints.restore_latest(mission)
            mission.append_adaptation("rollback", reason="repeated_failures")

    async def _handle_task_failure(self, app: Any, mission: Mission, task: TaskNode) -> dict[str, Any]:
        task.retry_count += 1
        if task.retry_count >= mission.max_retries:
            mission.task_graph.update_status(task.id, TaskNodeStatus.FAILED, reason="max_retries")
            self._metrics["tasks_failed"] += 1
            return {"success": False, "recovered": False}

        if self._confidence and self._confidence.replan_frequency_boost(mission.mission_id):
            self._planner.replan(mission, reason="low_confidence")
            mission.append_adaptation("replan", reason="confidence_decay")
            self._metrics["recoveries"] += 1

        mission.task_graph.update_status(task.id, TaskNodeStatus.PENDING, reason="retry")
        self._metrics["retries"] += 1
        if hasattr(app, "observability") and app.observability:
            from odin_backend.core.observability.events import TraceEventKind

            app.observability.tracer.record(
                TraceEventKind.RETRY_TRIGGERED,
                message="task retry",
                payload={"task_id": task.id, "retry_count": task.retry_count},
                component="mission_runtime",
            )
            app.observability.metrics.record_retry(mission_id=mission.mission_id)
        return {"success": False, "recovered": True}

    async def _execute_task(self, app: Any, mission: Mission, task: TaskNode) -> bool:
        if hasattr(app, "mission_execution_bridge") and getattr(
            app.settings, "mission_execution_bridge_enabled", True
        ):
            return await app.mission_execution_bridge.execute_task(mission, task)

        tool = task.output.get("tool", "noop")
        if mission.execution_strategy in ("conservative_readonly", "sandbox_only"):
            tool = "noop"

        if tool == "noop":
            mission.append_history("task_noop_complete", {"task_id": task.id, "goal": task.goal})
            return True

        from odin_backend.core.governor.decisions import ExecutionRequest

        request = ExecutionRequest(
            tool_name=tool,
            agent_id=task.assigned_agent or "odin",
            params=task.output.get("params", {}),
            workflow_id=mission.mission_id,
            task_id=task.id,
            user_confirmed=mission.human_approved,
        )

        gate = app.adaptive_policy if hasattr(app, "adaptive_policy") else app.execution_gate
        if hasattr(gate, "validate"):
            gate_result = gate.validate(app, request)
            from odin_backend.core.execution_gate.gate import GateDecision

            if gate_result.decision != GateDecision.ALLOW:
                return False

        result = await app.execution_contract.run_tool_pipeline(app, request, skip_stability=True)
        mission.append_history(
            "task_executed",
            {"task_id": task.id, "tool": tool, "success": result.success},
        )
        return result.success

    async def _evaluate_completion(
        self,
        app: Any,
        mission: Mission,
        *,
        wave_results: list[dict] | None = None,
    ) -> dict[str, Any]:
        sm = MissionStateMachine(mission)
        mission.sync_task_lists()
        nodes = list(mission.task_graph.nodes.values())
        if not nodes:
            sm.transition(MissionLifecycle.FAILED, reason="empty_graph")
            await app.mission_manager.persist(mission)
            return {"state": mission.current_state.value, "reason": "empty_graph"}

        pending = [n for n in nodes if n.status in (TaskNodeStatus.PENDING, TaskNodeStatus.READY)]
        executing = [
            n
            for n in nodes
            if n.status in (TaskNodeStatus.EXECUTING, TaskNodeStatus.RUNNING, TaskNodeStatus.ASSIGNED)
        ]
        failed = [n for n in nodes if n.status == TaskNodeStatus.FAILED]
        blocked = [n for n in nodes if n.status == TaskNodeStatus.BLOCKED]

        if self._confidence and self._confidence.should_escalate(mission.mission_id):
            sm.transition(MissionLifecycle.ESCALATED, reason="confidence_threshold")
            mission.append_adaptation("escalate", reason="confidence_threshold")
            await app.mission_manager.persist(mission)
            return {"state": "escalated", "reason": "low_confidence"}

        if failed and not pending and not executing:
            if mission.retry_count < mission.max_retries:
                mission.retry_count += 1
                self._planner.replan(mission, reason="failures_detected")
                sm.transition(MissionLifecycle.RETRYING, reason="failures_detected")
                sm.transition(MissionLifecycle.RUNNING, reason="replanned")
                mission.append_adaptation("replan", reason="failures_detected")
                self._metrics["recoveries"] += 1
                await app.mission_manager.persist(mission)
                return {
                    "state": mission.current_state.value,
                    "replanned": True,
                    "nodes": len(mission.task_graph.nodes),
                }
            sm.transition(MissionLifecycle.FAILED, reason="failures_exhausted")
            mission.append_history("mission_failed", {"failed_tasks": len(failed)})
            await app.mission_manager.persist(mission)
            return {"state": mission.current_state.value, "failed": len(failed)}

        if blocked and sm.state == MissionLifecycle.ESCALATED:
            await app.mission_manager.persist(mission)
            return {"state": "escalated", "blocked": len(blocked)}

        if not pending and not executing:
            sm.transition(MissionLifecycle.COMPLETED, reason="all_tasks_done")
            mission.metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
            mission.append_history("mission_completed", {"tasks": len(mission.completed_tasks)})
            await self._memory.link_mission_complete(mission.mission_id, mission.objective)
            exp = getattr(app, "experience_engine", None)
            if exp:
                await exp.on_mission_completed(mission)
            await app.mission_manager.persist(mission)
            return {"state": mission.current_state.value, "completed": True}

        if not mission.task_graph.ready_nodes():
            if sm.state == MissionLifecycle.RUNNING:
                sm.transition(MissionLifecycle.BLOCKED, reason="waiting_dependencies")
        elif sm.state in (MissionLifecycle.BLOCKED, MissionLifecycle.RETRYING):
            sm.transition(MissionLifecycle.RUNNING, reason="ready_tasks")

        await app.mission_manager.persist(mission)
        return {
            "state": migrate_legacy_state(mission.current_state).value,
            "pending": len(pending),
            "wave_results": wave_results or [],
        }

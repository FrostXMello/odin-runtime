"""Built-in perception observers (execution, environment, state)."""

from typing import Any

from odin_backend.models.perception import PerceptionCategory, PerceptionRecord


class ExecutionObserver:
    """Observes tool/contract execution outcomes."""

    def observe_execution(
        self,
        *,
        tool: str,
        success: bool,
        mission_id: str | None = None,
        task_id: str | None = None,
        output: dict | None = None,
    ) -> PerceptionRecord:
        category = (
            PerceptionCategory.EXECUTION_RESULT
            if success
            else PerceptionCategory.FAILURE_DETECTED
        )
        return PerceptionRecord(
            category=category,
            source="execution_observer",
            mission_id=mission_id,
            task_id=task_id,
            tool=tool,
            summary=f"Execution {'ok' if success else 'failed'}: {tool}",
            payload=output or {},
            confidence_impact=0.05 if success else -0.1,
        )


class EnvironmentObserver:
    """Observes runtime/environment snapshots."""

    def observe_environment(self, snapshot: dict[str, Any]) -> PerceptionRecord:
        degraded = snapshot.get("degraded") or snapshot.get("status") == "degraded"
        category = (
            PerceptionCategory.RESOURCE_WARNING
            if degraded
            else PerceptionCategory.ENVIRONMENT_CHANGE
        )
        return PerceptionRecord(
            category=category,
            source="environment_observer",
            summary=f"Environment {'degraded' if degraded else 'updated'}",
            payload=snapshot,
            confidence_impact=-0.05 if degraded else 0.0,
        )


class StateInterpreter:
    """Interprets mission/kernel state into perceptions."""

    def interpret_mission_progress(
        self,
        mission_id: str,
        state: str,
        *,
        pending: int = 0,
        failed: int = 0,
    ) -> PerceptionRecord:
        category = PerceptionCategory.MISSION_FEEDBACK
        if failed > 0:
            category = PerceptionCategory.FAILURE_DETECTED
        return PerceptionRecord(
            category=category,
            source="state_interpreter",
            mission_id=mission_id,
            summary=f"Mission {state} pending={pending} failed={failed}",
            payload={"state": state, "pending": pending, "failed": failed},
        )

    def interpret_goal_drift(
        self,
        mission_id: str,
        objective: str,
        focus: str,
    ) -> PerceptionRecord | None:
        if not focus or focus.lower()[:40] in objective.lower():
            return None
        return PerceptionRecord(
            category=PerceptionCategory.GOAL_DRIFT,
            source="state_interpreter",
            mission_id=mission_id,
            summary="Focus diverged from mission objective",
            payload={"objective": objective[:100], "focus": focus[:100]},
            confidence_impact=-0.08,
        )

"""Post-execution hooks — graph updates, dependency release, streaming."""

from __future__ import annotations

from typing import Any

from odin_backend.core.execution.models import ExecutionRecord, ExecutionState
from odin_backend.core.observability.events import TraceEventKind
from odin_backend.models.task_graph import TaskNode, TaskNodeStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_SUCCESS = {ExecutionState.COMPLETED}
_FAIL = {ExecutionState.FAILED, ExecutionState.TIMED_OUT, ExecutionState.CANCELLED}


class ExecutionCompletionHooks:
    def __init__(self, bridge: Any) -> None:
        self._bridge = bridge

    async def on_execution_finished(
        self,
        app: Any,
        ctx: Any,
        record: ExecutionRecord,
    ) -> dict[str, Any]:
        mission = ctx.mission
        task = ctx.task
        success = record.state in _SUCCESS

        task.output["execution_id"] = record.execution_id
        task.output["execution_state"] = record.state.value
        task.output["exit_code"] = record.exit_code
        if record.error:
            task.output["execution_error"] = record.error

        released = self._release_dependents(mission, task.id, success=success)
        if released:
            await self._emit_dependency_release(app, mission.mission_id, released, task_id=task.id)

        return {
            "success": success,
            "execution_id": record.execution_id,
            "state": record.state.value,
            "dependents_released": released,
        }

    def _release_dependents(self, mission: Any, completed_task_id: str, *, success: bool) -> list[str]:
        if not success:
            return []
        released: list[str] = []
        completed = {
            nid
            for nid, n in mission.task_graph.nodes.items()
            if n.status in (TaskNodeStatus.COMPLETE, TaskNodeStatus.SKIPPED)
        }
        completed.add(completed_task_id)
        for node in mission.task_graph.nodes.values():
            if completed_task_id not in node.dependencies:
                continue
            if all(dep in completed for dep in node.dependencies):
                if node.status == TaskNodeStatus.PENDING:
                    node.status = TaskNodeStatus.READY
                    released.append(node.id)
        return released

    async def _emit_dependency_release(
        self,
        app: Any,
        mission_id: str,
        task_ids: list[str],
        *,
        task_id: str | None = None,
    ) -> None:
        obs = getattr(app, "observability", None)
        if not obs:
            return
        obs.tracer.record(
            TraceEventKind.DEPENDENCY_RELEASED,
            message="dependency_release",
            payload={"mission_id": mission_id, "released_tasks": task_ids},
            component="mission_execution_bridge",
        )
        from odin_backend.core.streaming.bridge import get_stream_bridge
        from odin_backend.core.streaming.serializers import StreamEnvelope, StreamEventKind

        bridge = get_stream_bridge()
        if bridge:
            bridge.bus.publish_nowait(
                StreamEnvelope(
                    event_type=StreamEventKind.DEPENDENCY_RELEASED,
                    channel=f"mission:{mission_id}",
                    mission_id=mission_id,
                    task_id=task_id,
                    message=f"dependencies released: {len(task_ids)}",
                    payload={"released_tasks": task_ids, "kind": "dependency_release"},
                    component="mission_execution_bridge",
                )
            )

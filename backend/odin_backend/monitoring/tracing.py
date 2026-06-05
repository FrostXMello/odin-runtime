"""Workflow and tool execution tracing."""

from datetime import datetime, timezone
from typing import Any

from odin_backend.models.execution import ExecutionTrace
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class TraceManager:
    def __init__(self) -> None:
        self._traces: dict[str, ExecutionTrace] = {}
        self._workflow_traces: dict[str, list[str]] = {}

    def start_trace(
        self,
        *,
        tool_name: str | None = None,
        task_id: str | None = None,
        agent_id: str | None = None,
        workflow_id: str | None = None,
        correlation_id: str | None = None,
    ) -> ExecutionTrace:
        trace = ExecutionTrace(
            workflow_id=workflow_id,
            task_id=task_id,
            agent_id=agent_id,
            tool_name=tool_name,
        )
        if correlation_id:
            trace.events.append(f"correlation:{correlation_id}")
        self._traces[trace.trace_id] = trace
        if workflow_id:
            self._workflow_traces.setdefault(workflow_id, []).append(trace.trace_id)
        logger.debug("trace_started", trace_id=trace.trace_id, tool=tool_name)
        return trace

    def end_trace(self, trace: ExecutionTrace, *, success: bool) -> None:
        trace.ended_at = datetime.now(timezone.utc)
        trace.success = success
        trace.events.append("completed" if success else "failed")

    def get_trace(self, trace_id: str) -> ExecutionTrace | None:
        return self._traces.get(trace_id)

    def get_workflow_trace(self, workflow_id: str) -> list[ExecutionTrace]:
        ids = self._workflow_traces.get(workflow_id, [])
        return [self._traces[tid] for tid in ids if tid in self._traces]

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        traces = sorted(
            self._traces.values(),
            key=lambda t: t.started_at,
            reverse=True,
        )[:limit]
        return [t.model_dump(mode="json") for t in traces]

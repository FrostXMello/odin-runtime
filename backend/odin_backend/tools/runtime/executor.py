"""Production tool executor with tracing, timeout, audit."""

import asyncio
import time
from typing import Any

from odin_backend.events.bus import EventBus
from typing import TYPE_CHECKING

from odin_backend.shared.contracts.governance import ExecutionRequest, GovernorDecisionType

if TYPE_CHECKING:
    from odin_backend.core.governor.governor import ExecutionGovernor
from odin_backend.policies.engine import PolicyEngine
from odin_backend.models.event import Event, EventType
from odin_backend.models.execution import ToolExecutionResult
from odin_backend.monitoring.audit import AuditLogger
from odin_backend.monitoring.tracing import TraceManager
from odin_backend.permissions.heimdall import HeimdallService
from odin_backend.tools.base import ToolContext
from odin_backend.tools.registry import ToolRegistry
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT = 120.0
MAX_RETRIES = 2


class RuntimeToolExecutor:
    """All tool execution: permissions → trace → execute → audit → events."""

    def __init__(
        self,
        registry: ToolRegistry,
        event_bus: EventBus,
        heimdall: HeimdallService,
        trace_manager: TraceManager,
        audit: AuditLogger,
    ) -> None:
        self._registry = registry
        self._event_bus = event_bus
        self._heimdall = heimdall
        self._trace = trace_manager
        self._audit = audit
        self._policy: PolicyEngine | None = None
        self._governor: "ExecutionGovernor | None" = None

    def set_policy_engine(self, policy: PolicyEngine) -> None:
        self._policy = policy

    def set_governor(self, governor: "ExecutionGovernor") -> None:
        self._governor = governor

    async def execute(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: ToolContext,
        *,
        timeout: float | None = None,
        skip_governor: bool = False,
    ) -> ToolExecutionResult:
        trace = self._trace.start_trace(
            tool_name=tool_name,
            task_id=context.task_id,
            agent_id=str(context.agent_id),
            correlation_id=context.correlation_id,
        )

        tool = self._registry.get(tool_name)
        if tool is None:
            result = ToolExecutionResult(
                success=False,
                errors=[f"Unknown tool: {tool_name}"],
                trace_id=trace.trace_id,
            )
            await self._finish(trace, tool_name, context, result)
            return result

        if self._governor and not skip_governor:
            gov_req = ExecutionRequest(
                tool_name=tool_name,
                agent_id=str(context.agent_id),
                params=params,
                workflow_id=context.correlation_id,
                task_id=context.task_id,
                user_confirmed=context.user_confirmed,
            )
            gov_decision = await self._governor.evaluate(gov_req)
            if gov_decision.decision != GovernorDecisionType.APPROVE:
                result = ToolExecutionResult(
                    success=False,
                    errors=[f"Governor {gov_decision.decision.value}: {gov_decision.reason}"],
                    trace_id=trace.trace_id,
                )
                await self._finish(trace, tool_name, context, result, denied=True)
                return result

        if self._policy:
            policy_decision = await self._policy.evaluate(
                tool_name,
                params=params,
                workflow_id=context.correlation_id,
                agent_id=context.agent_id,
            )
            if not policy_decision.allowed:
                result = ToolExecutionResult(
                    success=False,
                    errors=[policy_decision.reason],
                    trace_id=trace.trace_id,
                )
                await self._finish(trace, tool_name, context, result, denied=True)
                return result

        decision = await self._heimdall.check_and_audit(
            tool_name, context.agent_id, user_confirmed=context.user_confirmed
        )

        if not decision.allowed:
            if decision.requires_confirmation:
                await self._event_bus.publish(
                    Event(
                        type=EventType.PERMISSION_REQUESTED,
                        source=context.agent_id,
                        task_id=context.task_id,
                        correlation_id=context.correlation_id,
                        payload={
                            "tool": tool_name,
                            "permission_class": decision.permission_class.value,
                        },
                    )
                )
            result = ToolExecutionResult(
                success=False,
                errors=[decision.reason],
                trace_id=trace.trace_id,
            )
            await self._finish(trace, tool_name, context, result, denied=True)
            return result

        last_error: str | None = None
        for attempt in range(MAX_RETRIES + 1):
            start = time.perf_counter()
            try:
                legacy = await asyncio.wait_for(
                    tool.execute(params, context),
                    timeout=timeout or DEFAULT_TIMEOUT,
                )
                elapsed = time.perf_counter() - start
                result = ToolExecutionResult(
                    success=legacy.success,
                    data=legacy.data,
                    logs=[f"attempt={attempt + 1}"],
                    errors=[legacy.error] if legacy.error else [],
                    execution_time=round(elapsed, 3),
                    trace_id=trace.trace_id,
                )
                await self._finish(trace, tool_name, context, result)
                return result
            except asyncio.TimeoutError:
                last_error = f"Tool '{tool_name}' timed out"
                trace.events.append("timeout")
            except Exception as exc:
                last_error = str(exc)
                logger.warning("tool_retry", tool=tool_name, attempt=attempt + 1)

        result = ToolExecutionResult(
            success=False,
            errors=[last_error or "Execution failed"],
            trace_id=trace.trace_id,
        )
        await self._finish(trace, tool_name, context, result, failed=True)
        return result

    async def _finish(
        self,
        trace: Any,
        tool_name: str,
        context: ToolContext,
        result: ToolExecutionResult,
        *,
        denied: bool = False,
        failed: bool = False,
    ) -> None:
        self._trace.end_trace(trace, success=result.success)
        await self._audit.log_tool_execution(tool_name, context, result)

        if denied:
            await self._event_bus.publish(
                Event(
                    type=EventType.TOOL_DENIED,
                    source=context.agent_id,
                    task_id=context.task_id,
                    payload={"tool": tool_name, "errors": result.errors},
                )
            )
        elif failed or not result.success:
            await self._event_bus.publish(
                Event(
                    type=EventType.TOOL_FAILED,
                    source=context.agent_id,
                    task_id=context.task_id,
                    payload={"tool": tool_name, "errors": result.errors},
                )
            )
        else:
            await self._event_bus.publish(
                Event(
                    type=EventType.TOOL_EXECUTED,
                    source=context.agent_id,
                    task_id=context.task_id,
                    payload={
                        "tool": tool_name,
                        "success": True,
                        "execution_time": result.execution_time,
                    },
                )
            )

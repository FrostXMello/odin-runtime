"""Tool executor — permission-aware execution layer."""

from typing import Any

from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.monitoring.logging import get_logger
from odin_backend.tools.base import ToolContext, ToolResult
from odin_backend.tools.registry import ToolRegistry

logger = get_logger(__name__)


class ToolExecutor:
    """Executes tools through registry with permission checks."""

    def __init__(self, registry: ToolRegistry, event_bus: EventBus) -> None:
        self._registry = registry
        self._event_bus = event_bus

    async def execute(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: ToolContext,
    ) -> ToolResult:
        tool = self._registry.get(tool_name)
        if tool is None:
            return ToolResult(success=False, error=f"Unknown tool: {tool_name}")

        decision = self._registry.permission_service.check(
            tool_name,
            context.agent_id,
            user_confirmed=context.user_confirmed,
        )

        if not decision.allowed:
            await self._event_bus.publish(
                Event(
                    type=EventType.TOOL_DENIED,
                    source=context.agent_id,
                    task_id=context.task_id,
                    correlation_id=context.correlation_id,
                    payload={
                        "tool": tool_name,
                        "reason": decision.reason,
                        "requires_confirmation": decision.requires_confirmation,
                    },
                )
            )
            return ToolResult(success=False, error=decision.reason)

        try:
            result = await tool.execute(params, context)
            await self._event_bus.publish(
                Event(
                    type=EventType.TOOL_EXECUTED,
                    source=context.agent_id,
                    task_id=context.task_id,
                    correlation_id=context.correlation_id,
                    payload={"tool": tool_name, "success": result.success},
                )
            )
            return result
        except Exception as exc:
            logger.exception("tool_execution_failed", tool=tool_name, error=str(exc))
            return ToolResult(success=False, error=str(exc))

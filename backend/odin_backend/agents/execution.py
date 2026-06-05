"""Agent execution mixin — uses runtime tool executor protocol (injected at bootstrap)."""

from typing import Any

from odin_backend.agents.protocols import ToolExecutorProtocol
from odin_backend.models.task import Task, TaskResult
from odin_backend.tools.base import ToolContext


class ToolExecutionMixin:
    """Execute task tools via injected executor — no concrete import at module load."""

    _tool_executor: ToolExecutorProtocol

    async def execute_tools_for_task(self, task: Task) -> TaskResult:
        output: dict[str, Any] = {
            "agent": self.agent_id,
            "task_id": task.id,
        }
        tool_name = task.payload.get("tool") or (
            task.required_tools[0] if task.required_tools else None
        )

        if not tool_name:
            output["message"] = f"{self.display_name} acknowledged task (no tool specified)"
            return TaskResult(success=True, output=output)

        params = task.payload.get("params", task.payload)
        ctx = ToolContext(
            task_id=task.id,
            agent_id=self.agent_id,
            user_confirmed=task.payload.get("user_confirmed", False),
        )
        result = await self._tool_executor.execute(tool_name, params, ctx)
        output[tool_name] = result.model_dump()
        return TaskResult(success=result.success, output=output, error=result.errors[0] if result.errors else None)

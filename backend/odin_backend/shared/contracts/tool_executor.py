"""
Tool executor protocol — agents depend on this, not on RuntimeToolExecutor.

Circular import occurred because agents.base imported the concrete executor,
which imported core.governor.decisions, which loaded core/__init__.py → core.app
→ agents.registry → agents.base (partial).
"""

from typing import Any, Protocol, runtime_checkable

from odin_backend.models.execution import ToolExecutionResult
from odin_backend.tools.base import ToolContext


@runtime_checkable
class ToolExecutorProtocol(Protocol):
    """Runtime tool execution surface injected at app bootstrap."""

    async def execute(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: ToolContext,
        *,
        timeout: float | None = None,
        skip_governor: bool = False,
    ) -> ToolExecutionResult: ...

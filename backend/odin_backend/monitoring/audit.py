"""Security audit logging for tool and permission actions."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from odin_backend.models.execution import ToolExecutionResult
from odin_backend.monitoring.logging import get_logger

if TYPE_CHECKING:
    from odin_backend.tools.base import ToolContext

logger = get_logger(__name__)


class AuditLogger:
    def __init__(self, max_entries: int = 2000) -> None:
        self._entries: list[dict[str, Any]] = []
        self._max = max_entries

    async def log_tool_execution(
        self, tool_name: str, context: "ToolContext", result: ToolExecutionResult
    ) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "tool_execution",
            "tool": tool_name,
            "agent": str(context.agent_id),
            "task_id": context.task_id,
            "success": result.success,
            "execution_time": result.execution_time,
            "errors": result.errors,
        }
        self._append(entry)
        logger.info("audit_tool", **{k: v for k, v in entry.items() if k != "type"})

    async def log_permission(
        self, tool_name: str, agent_id: str, allowed: bool, reason: str = ""
    ) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "permission_check",
            "tool": tool_name,
            "agent": agent_id,
            "allowed": allowed,
            "reason": reason,
        }
        self._append(entry)

    def _append(self, entry: dict[str, Any]) -> None:
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]

    def get_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return list(reversed(self._entries[-limit:]))

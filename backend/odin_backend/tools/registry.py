"""Tool registry — central catalog of capabilities."""

from odin_backend.monitoring.logging import get_logger
from odin_backend.permissions.models import PermissionClass
from odin_backend.permissions.service import PermissionService
from odin_backend.tools.base import Tool

logger = get_logger(__name__)


class ToolRegistry:
    """Registers and resolves tools by name."""

    def __init__(self, permission_service: PermissionService | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        self._permission_service = permission_service or PermissionService()

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            logger.warning("tool_overwrite", tool_name=tool.name)
        self._tools[tool.name] = tool
        self._permission_service.register_tool_permission(tool.name, tool.permission_class)
        logger.info("tool_registered", tool_name=tool.name)

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        return [tool.get_schema() for tool in self._tools.values()]

    def has(self, name: str) -> bool:
        return name in self._tools

    @property
    def permission_service(self) -> PermissionService:
        return self._permission_service

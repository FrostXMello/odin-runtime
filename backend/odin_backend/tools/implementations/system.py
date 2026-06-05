"""System information tools."""

import platform
from typing import Any

from odin_backend.permissions.models import PermissionClass
from odin_backend.tools.base import Tool, ToolContext, ToolResult


class GetSystemInfoTool(Tool):
    name = "get_system_info"
    description = "Get basic system information"
    permission_class = PermissionClass.SAFE

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "platform": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python": platform.python_version(),
                "processor": platform.processor() or "unknown",
            },
        )

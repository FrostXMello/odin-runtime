"""Built-in stub tools — foundation placeholders."""

from typing import Any

from odin_backend.permissions.models import PermissionClass
from odin_backend.tools.base import Tool, ToolContext, ToolResult


class ReadFileTool(Tool):
    name = "read_file"
    description = "Read contents of a local file"
    permission_class = PermissionClass.SAFE

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        path = params.get("path", "")
        return ToolResult(success=True, data={"path": path, "content": "", "stub": True})


class WriteFileTool(Tool):
    name = "write_file"
    description = "Write contents to a local file"
    permission_class = PermissionClass.CONFIRM_REQUIRED

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={"path": params.get("path", ""), "written": False, "stub": True},
        )


class SearchWebTool(Tool):
    name = "search_web"
    description = "Search the web for information"
    permission_class = PermissionClass.SAFE

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        query = params.get("query", "")
        return ToolResult(success=True, data={"query": query, "results": [], "stub": True})


class ExecuteTerminalTool(Tool):
    name = "execute_terminal"
    description = "Execute a shell command"
    permission_class = PermissionClass.RESTRICTED

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={"command": params.get("command", ""), "stdout": "", "stub": True},
        )


class TakeScreenshotTool(Tool):
    name = "take_screenshot"
    description = "Capture desktop screenshot"
    permission_class = PermissionClass.CONFIRM_REQUIRED

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={"path": None, "stub": True})


def register_builtin_tools(registry) -> None:
    for tool_cls in (
        ReadFileTool,
        WriteFileTool,
        SearchWebTool,
        ExecuteTerminalTool,
        TakeScreenshotTool,
    ):
        registry.register(tool_cls())

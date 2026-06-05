"""Register all production tools."""

from odin_backend.tools.implementations.browser import (
    ExtractTabContentTool,
    GetBrowserTabsTool,
    OpenBrowserTool,
)
from odin_backend.tools.implementations.content import GenerateEmailTool, SummarizeContentTool
from odin_backend.tools.implementations.email import SendEmailTool
from odin_backend.tools.implementations.filesystem import (
    ListDirectoryTool,
    ReadFileTool,
    WriteFileTool,
)
from odin_backend.tools.implementations.system import GetSystemInfoTool
from odin_backend.tools.implementations.terminal import ExecuteTerminalTool
from odin_backend.tools.implementations.web import SearchWebTool
from odin_backend.tools.registry import ToolRegistry


def register_all_tools(registry: ToolRegistry) -> None:
    for tool_cls in (
        ReadFileTool,
        WriteFileTool,
        ListDirectoryTool,
        GetSystemInfoTool,
        SearchWebTool,
        ExecuteTerminalTool,
        OpenBrowserTool,
        GetBrowserTabsTool,
        ExtractTabContentTool,
        SummarizeContentTool,
        GenerateEmailTool,
        SendEmailTool,
    ):
        registry.register(tool_cls())

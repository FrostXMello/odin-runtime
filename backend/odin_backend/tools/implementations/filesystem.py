"""Filesystem tools — safe read/write/list."""

from pathlib import Path
from typing import Any

from odin_backend.permissions.models import PermissionClass
from odin_backend.tools.base import Tool, ToolContext, ToolResult

# Sandbox: only paths under user home or explicit allowed roots
def _resolve_safe(path_str: str) -> Path:
    p = Path(path_str).expanduser().resolve()
    home = Path.home().resolve()
    if not str(p).startswith(str(home)):
        raise PermissionError(f"Path outside allowed sandbox: {p}")
    return p


class ReadFileTool(Tool):
    name = "read_file"
    description = "Read contents of a local file"
    permission_class = PermissionClass.SAFE

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        try:
            path = _resolve_safe(params["path"])
            if not path.is_file():
                return ToolResult(success=False, error=f"Not a file: {path}")
            content = path.read_text(encoding="utf-8", errors="replace")
            return ToolResult(success=True, data={"path": str(path), "content": content[:50000]})
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class WriteFileTool(Tool):
    name = "write_file"
    description = "Write contents to a local file"
    permission_class = PermissionClass.CONFIRM_REQUIRED

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        try:
            path = _resolve_safe(params["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(params.get("content", ""), encoding="utf-8")
            return ToolResult(success=True, data={"path": str(path), "written": True})
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class ListDirectoryTool(Tool):
    name = "list_directory"
    description = "List files in a directory"
    permission_class = PermissionClass.SAFE

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        try:
            path = _resolve_safe(params.get("path", "."))
            if not path.is_dir():
                return ToolResult(success=False, error=f"Not a directory: {path}")
            entries = [
                {"name": e.name, "is_dir": e.is_dir()}
                for e in sorted(path.iterdir())[:200]
            ]
            return ToolResult(success=True, data={"path": str(path), "entries": entries})
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))

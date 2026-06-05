"""Controlled terminal execution."""

import asyncio
import shlex
from typing import Any

from odin_backend.permissions.models import PermissionClass
from odin_backend.tools.base import Tool, ToolContext, ToolResult

BLOCKED_PATTERNS = ("rm -rf", "format", "del /f", "shutdown", "reboot", ":(){", "mkfs")


class ExecuteTerminalTool(Tool):
    name = "execute_terminal"
    description = "Execute a shell command (sandboxed)"
    permission_class = PermissionClass.RESTRICTED

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        command = params.get("command", "").strip()
        if not command:
            return ToolResult(success=False, error="command required")

        lower = command.lower()
        for blocked in BLOCKED_PATTERNS:
            if blocked in lower:
                return ToolResult(success=False, error=f"Blocked command pattern: {blocked}")

        timeout = min(int(params.get("timeout", 30)), 60)
        try:
            if hasattr(asyncio, "create_subprocess_shell"):
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                parts = shlex.split(command)
                proc = await asyncio.create_subprocess_exec(
                    *parts,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return ToolResult(
                success=proc.returncode == 0,
                data={
                    "command": command,
                    "stdout": stdout.decode(errors="replace")[:10000],
                    "stderr": stderr.decode(errors="replace")[:5000],
                    "returncode": proc.returncode,
                },
                error=None if proc.returncode == 0 else f"exit {proc.returncode}",
            )
        except asyncio.TimeoutError:
            return ToolResult(success=False, error=f"Command timed out after {timeout}s")
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))

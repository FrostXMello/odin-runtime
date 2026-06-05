"""Specialized executors — all route through governed live pipeline."""

from typing import Any

from odin_backend.tools.execution.pipeline import LiveToolPipeline

READ_TOOLS = frozenset({"read_file", "list_directory", "get_system_info"})
WRITE_TOOLS = frozenset({"write_file"})
OS_TOOLS = frozenset({"execute_terminal"})
BROWSER_TOOLS = frozenset({"open_browser", "get_browser_tabs", "extract_tab_content"})


class _BaseExecutor:
    category: str = "generic"

    async def run(
        self,
        app: Any,
        tool_name: str,
        params: dict,
        *,
        user_confirmed: bool = False,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        pipeline = LiveToolPipeline()
        return await pipeline.execute_with_trace(
            app,
            tool_name,
            params,
            agent_id="valkyrie",
            task_id=task_id,
            user_confirmed=user_confirmed,
            category=self.category,
        )


class FileSystemExecutor(_BaseExecutor):
    category = "filesystem"

    async def read(self, app: Any, path: str) -> dict[str, Any]:
        return await self.run(app, "read_file", {"path": path})

    async def list_dir(self, app: Any, path: str = ".") -> dict[str, Any]:
        return await self.run(app, "list_directory", {"path": path})

    async def write(
        self, app: Any, path: str, content: str, *, user_confirmed: bool = True
    ) -> dict[str, Any]:
        return await self.run(
            app, "write_file", {"path": path, "content": content}, user_confirmed=user_confirmed
        )


class OSCommandExecutor(_BaseExecutor):
    category = "os_command"

    async def run_command(
        self, app: Any, command: str, *, user_confirmed: bool = True
    ) -> dict[str, Any]:
        return await self.run(
            app, "execute_terminal", {"command": command}, user_confirmed=user_confirmed
        )


class BrowserAutomationExecutor(_BaseExecutor):
    category = "browser"

    async def open_url(self, app: Any, url: str, *, user_confirmed: bool = False) -> dict[str, Any]:
        return await self.run(app, "open_browser", {"url": url}, user_confirmed=user_confirmed)

    async def list_tabs(self, app: Any) -> dict[str, Any]:
        return await self.run(app, "get_browser_tabs", {})


class ClipboardExecutor(_BaseExecutor):
    """Clipboard via summarize/read pipeline — no direct OS clipboard API."""

    category = "clipboard"

    async def capture_via_read(self, app: Any, path: str) -> dict[str, Any]:
        return await self.run(app, "read_file", {"path": path})

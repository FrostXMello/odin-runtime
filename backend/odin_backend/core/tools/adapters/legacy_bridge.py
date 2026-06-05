"""Bridge intelligent tool registry to odin_backend.tools runtime."""

from __future__ import annotations

from typing import Any


class LegacyToolBridge:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def execute(
        self,
        tool_name: str,
        params: dict[str, Any],
        *,
        agent_id: str = "brokk",
    ) -> dict[str, Any]:
        from odin_backend.tools.base import ToolContext
        from odin_backend.models.task import AgentId

        try:
            agent = AgentId(agent_id)
        except ValueError:
            agent = AgentId.BROKK
        ctx = ToolContext(agent_id=agent)
        result = await self._app.tool_executor.execute(tool_name, params, ctx, skip_governor=True)
        return {"success": result.success, "data": result.data, "errors": result.errors}

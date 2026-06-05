"""Tool registry API."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from odin_backend.models.task import AgentId
from odin_backend.tools.base import ToolContext

router = APIRouter(prefix="/tools", tags=["tools"])


class ToolExecuteRequest(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)
    agent_id: AgentId = AgentId.ODIN
    task_id: str | None = None
    user_confirmed: bool = False


@router.get("")
async def list_tools(request: Request) -> list[dict]:
    app = request.app.state.odin
    return app.tool_registry.list_tools()


@router.post("/{tool_name}/execute")
async def execute_tool(tool_name: str, body: ToolExecuteRequest, request: Request) -> dict:
    app = request.app.state.odin
    if not app.tool_registry.has(tool_name):
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    ctx = ToolContext(
        task_id=body.task_id,
        agent_id=body.agent_id,
        user_confirmed=body.user_confirmed,
    )
    result = await app.tool_executor.execute(tool_name, body.params, ctx)
    return {
        "success": result.success,
        "data": result.data,
        "logs": result.logs,
        "errors": result.errors,
        "execution_time": result.execution_time,
    }

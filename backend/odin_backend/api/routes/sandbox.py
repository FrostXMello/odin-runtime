"""Sandbox execution API."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from odin_backend.models.task import AgentId
from odin_backend.sandbox.profiles import SandboxProfile
from odin_backend.tools.base import ToolContext

router = APIRouter(prefix="/sandbox", tags=["sandbox"])


class SandboxExecuteRequest(BaseModel):
    profile: SandboxProfile = SandboxProfile.DEV_SANDBOX
    tool_name: str
    params: dict = {}
    user_confirmed: bool = False


@router.get("/snapshots")
async def list_snapshots(request: Request) -> list[dict]:
    app = request.app.state.odin
    return app.sandbox.list_snapshots()


@router.post("/execute")
async def sandbox_execute(body: SandboxExecuteRequest, request: Request) -> dict:
    app = request.app.state.odin
    ctx = ToolContext(agent_id=AgentId.BROKK, user_confirmed=body.user_confirmed)
    return await app.sandbox.execute_in_sandbox(
        body.profile, body.tool_name, body.params, ctx
    )

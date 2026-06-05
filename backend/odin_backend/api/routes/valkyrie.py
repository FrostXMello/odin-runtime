"""VALKYRIE execution API."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/valkyrie", tags=["valkyrie"])


class ToolExecuteBody(BaseModel):
    tool_name: str
    params: dict = Field(default_factory=dict)
    user_confirmed: bool = False


class ToolChainBody(BaseModel):
    steps: list[dict]
    user_confirmed: bool = False


@router.get("/status")
async def valkyrie_status(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "valkyrie_enabled": app.env_config.valkyrie_enabled,
        "desktop_control_enabled": app.env_config.desktop_control_enabled,
        "environment": app.env_config.snapshot(),
    }


@router.post("/execute")
async def execute_tool(body: ToolExecuteBody, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.valkyrie.execute_task(
        tool_name=body.tool_name,
        params=body.params,
        user_confirmed=body.user_confirmed,
    )
    return result.model_dump(mode="json")


@router.post("/chain")
async def execute_chain(body: ToolChainBody, request: Request) -> list[dict]:
    app = request.app.state.odin
    results = await app.valkyrie.execute_tool_chain(
        body.steps, user_confirmed=body.user_confirmed
    )
    return [r.model_dump(mode="json") for r in results]

"""Milestone 9 — data contracts & agent protocol API."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from odin_backend.core.governor.decisions import ExecutionRequest
from odin_backend.models.agent_message import AgentMessage, AgentMessageType
from odin_backend.models.task import TaskCreate

router = APIRouter(prefix="/protocol", tags=["protocol"])


class AgentMessageBody(BaseModel):
    from_agent: str
    type: AgentMessageType
    payload: dict = Field(default_factory=dict)
    task_id: str = ""
    confidence: float = 1.0
    requires_escalation: bool = False


class TaskAssignBody(BaseModel):
    goal: str
    agent_id: str
    task_id: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    priority: int = 50


class PipelineToolBody(BaseModel):
    tool_name: str
    agent_id: str = "odin"
    params: dict = Field(default_factory=dict)
    workflow_id: str | None = None
    user_confirmed: bool = False


@router.get("/state/schema")
async def cognitive_state_schema(request: Request) -> dict:
    """Return current cognitive state (Prompt 9 SSOT)."""
    app = request.app.state.odin
    return app.kernel.get_state().model_dump(mode="json")


@router.get("/task-graph")
async def get_task_graph(request: Request) -> dict:
    app = request.app.state.odin
    return app.kernel.task_graph.snapshot()


@router.post("/agent/message")
async def agent_message(body: AgentMessageBody, request: Request) -> dict:
    app = request.app.state.odin
    msg = AgentMessage(
        from_agent=body.from_agent,
        type=body.type,
        payload=body.payload,
        task_id=body.task_id,
        confidence=body.confidence,
        requires_escalation=body.requires_escalation,
    )
    return await app.agent_protocol.receive_from_agent(msg)


@router.post("/agent/assign")
async def assign_task(body: TaskAssignBody, request: Request) -> dict:
    app = request.app.state.odin
    node = await app.agent_protocol.assign_task(
        goal=body.goal,
        agent_id=body.agent_id,
        task_id=body.task_id,
        dependencies=body.dependencies,
        priority=body.priority,
    )
    return node.model_dump(mode="json")


@router.post("/execution/pipeline")
async def run_execution_pipeline(body: PipelineToolBody, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.execution_contract.run_tool_pipeline(
        app,
        ExecutionRequest(
            tool_name=body.tool_name,
            agent_id=body.agent_id,
            params=body.params,
            workflow_id=body.workflow_id,
            user_confirmed=body.user_confirmed,
        ),
    )
    return result.model_dump()


@router.post("/tasks/submit")
async def submit_task_graph(body: TaskCreate, request: Request) -> dict:
    app = request.app.state.odin
    task = await app.orchestrator.submit_task(body)
    node = app.kernel.task_graph.get(task.id)
    if not node:
        raise HTTPException(status_code=500, detail="Task graph node not created")
    return {"task": task.model_dump(mode="json"), "graph_node": node.model_dump(mode="json")}

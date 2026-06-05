"""Agent society APIs."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["society-runtime"])


class SpawnAgentRequest(BaseModel):
    name: str
    role: str = "generalist"
    capabilities: list[str] = Field(default_factory=list)
    expertise_domains: list[str] = Field(default_factory=list)


class CreateObjectiveRequest(BaseModel):
    owner_agent_id: str
    title: str


class StartDialogueRequest(BaseModel):
    topic: str
    participant_ids: list[str] = Field(default_factory=list)


class CreateDelegationRequest(BaseModel):
    from_agent: str
    to_agent: str
    task: str
    mission_id: str | None = None


@router.get("/society")
async def runtime_society(request: Request) -> dict:
    app = request.app.state.odin
    agents = await app.agent_society.list_agents()
    objectives = await app.agent_society._objectives.list_all()
    return {
        "snapshot": app.agent_society.snapshot(),
        "agent_count": len(agents),
        "objective_count": len(objectives),
        "patterns": app.peer_learning.patterns(),
    }


@router.get("/society/agents")
async def runtime_society_agents(request: Request) -> dict:
    app = request.app.state.odin
    society = await app.agent_society.list_agents()
    return {"society_agents": society, "agents": [a.get("name") for a in society]}


@router.post("/society/agents/spawn")
async def runtime_agents_spawn(body: SpawnAgentRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.agent_society.spawn_agent(
        name=body.name,
        role=body.role,
        capabilities=body.capabilities,
        expertise_domains=body.expertise_domains,
    )


@router.get("/society/collaboration")
async def runtime_society_collaboration(request: Request) -> dict:
    app = request.app.state.odin
    return {"society": app.agent_society.snapshot()}


@router.get("/society/objectives")
async def runtime_society_objectives(request: Request) -> dict:
    app = request.app.state.odin
    society_objs = await app.agent_society._objectives.list_all()
    return {"society_objectives": society_objs}


@router.post("/society/objectives/create")
async def runtime_objectives_create(body: CreateObjectiveRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.agent_society.create_objective(owner_agent_id=body.owner_agent_id, title=body.title)


@router.get("/society/dialogues")
async def runtime_dialogues(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "dialogues": app.agent_messages.dialogues(),
        "active_debates": app.agent_society._debates.list_active(),
    }


@router.post("/society/dialogues/start")
async def runtime_dialogues_start(body: StartDialogueRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.agent_society.start_dialogue(topic=body.topic, participant_ids=body.participant_ids)


@router.get("/society/delegation")
async def runtime_delegation(request: Request) -> dict:
    app = request.app.state.odin
    return {"delegations": app.agent_society._delegations.list_all()}


@router.post("/society/delegation/create")
async def runtime_delegation_create(body: CreateDelegationRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.agent_society.create_delegation(
        from_agent=body.from_agent, to_agent=body.to_agent, task=body.task, mission_id=body.mission_id
    )


@router.get("/society/expertise")
async def runtime_expertise(request: Request) -> dict:
    app = request.app.state.odin
    return {"heatmap": app.agent_society.expertise_heatmap(), "patterns": app.peer_learning.patterns()}

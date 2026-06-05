"""Federation, world simulation, strategy, and governance APIs."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["federation-runtime"])


class ConnectNodeRequest(BaseModel):
    name: str
    role: str = "worker"
    capabilities: list[str] = Field(default_factory=list)
    mode: str = "trusted_cluster"
    token: str | None = None


class DisconnectNodeRequest(BaseModel):
    node_id: str


class ProjectWorldRequest(BaseModel):
    scenario: str
    assumptions: list[str] = Field(default_factory=list)
    branches: int = 2


class PredictWorldRequest(BaseModel):
    entity: str
    hypothesis: str
    mission_id: str | None = None
    confidence: float = 0.6


class AnalyzeStrategyRequest(BaseModel):
    goal: str
    context: dict = Field(default_factory=dict)


class ShareMemoryRequest(BaseModel):
    from_node: str
    fact: str
    confidence: float = 0.7
    trust: float = 0.5


@router.get("/federation")
async def runtime_federation(request: Request) -> dict:
    app = request.app.state.odin
    return {"snapshot": app.federation_runtime.snapshot(), "society": app.society_federation.snapshot()}


@router.get("/federation/nodes")
async def runtime_federation_nodes(request: Request) -> dict:
    app = request.app.state.odin
    nodes = await app.federation_runtime.list_nodes()
    return {"nodes": nodes, "count": len(nodes)}


@router.get("/federation/topology")
async def runtime_federation_topology(request: Request) -> dict:
    app = request.app.state.odin
    return {"topology": app.federation_runtime.topology()}


@router.get("/federation/trust")
async def runtime_federation_trust(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "trust_map": app.federation_runtime.trust_map(),
        "governance": app.federation_governance.snapshot(),
    }


@router.post("/federation/connect")
async def runtime_federation_connect(body: ConnectNodeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.federation_runtime.connect_node(
        name=body.name,
        role=body.role,
        capabilities=body.capabilities,
        mode=body.mode,
        token=body.token,
    )


@router.post("/federation/disconnect")
async def runtime_federation_disconnect(body: DisconnectNodeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.federation_runtime.disconnect_node(body.node_id)


@router.get("/world")
async def runtime_world(request: Request) -> dict:
    app = request.app.state.odin
    return {"world": await app.world_simulation.snapshot()}


@router.get("/world/simulation")
async def runtime_world_simulation(request: Request) -> dict:
    app = request.app.state.odin
    return {"simulations": app.world_simulation.list_simulations()}


@router.post("/world/project")
async def runtime_world_project(body: ProjectWorldRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.world_simulation.project(
        scenario=body.scenario, assumptions=body.assumptions, branches=body.branches
    )


@router.post("/world/predict")
async def runtime_world_predict(body: PredictWorldRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.world_simulation.predict(
        entity=body.entity, hypothesis=body.hypothesis, mission_id=body.mission_id, confidence=body.confidence
    )


@router.get("/strategy")
async def runtime_strategy(request: Request) -> dict:
    app = request.app.state.odin
    return {"strategy": app.strategic_reasoning.snapshot()}


@router.post("/strategy/analyze")
async def runtime_strategy_analyze(body: AnalyzeStrategyRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.strategic_reasoning.analyze(goal=body.goal, context=body.context)


@router.get("/federated-memory")
async def runtime_federated_memory(request: Request) -> dict:
    app = request.app.state.odin
    memories = await app.federated_memory.list_memories()
    return {"memories": memories, "snapshot": app.federated_memory.snapshot()}


@router.post("/federated-memory/share")
async def runtime_federated_memory_share(body: ShareMemoryRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.federated_memory.share(
        from_node=body.from_node, fact=body.fact, confidence=body.confidence, trust=body.trust
    )


@router.get("/governance")
async def runtime_governance(request: Request) -> dict:
    app = request.app.state.odin
    return {"governance": app.federation_governance.snapshot()}


@router.post("/governance/quarantine/{node_id}")
async def runtime_governance_quarantine(node_id: str, request: Request) -> dict:
    app = request.app.state.odin
    return app.federation_governance.quarantine(node_id)

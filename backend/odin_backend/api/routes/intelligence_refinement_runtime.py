"""Intelligence refinement runtime APIs (Prompt 38)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["intelligence-refinement-runtime"])


class EvaluateRequest(BaseModel):
    text: str
    steps: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


class RetrieveRequest(BaseModel):
    query: str
    limit: int = 10
    project_id: str | None = None


class RepoAnalyzeRequest(BaseModel):
    path: str
    files: list[str] = Field(default_factory=list)


class PatchRequest(BaseModel):
    file_path: str
    goal: str
    content: str


class DebugRequest(BaseModel):
    error: str
    context: dict = Field(default_factory=dict)


class RouteRequest(BaseModel):
    task: str
    complexity: float = 0.5


class AssessTaskRequest(BaseModel):
    complexity: float
    action: str
    destructive: bool = False


class ResearchValidateRequest(BaseModel):
    claims: list[str]
    sources: list[str]


@router.get("/intelligence")
async def runtime_intelligence(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "quality": app.intelligence_quality.snapshot(),
        "operator": app.operator_intelligence.snapshot(),
        "autonomy": app.autonomy_reliability.snapshot(),
    }


@router.post("/intelligence/evaluate")
async def runtime_intelligence_evaluate(body: EvaluateRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.intelligence_quality.evaluate(text=body.text, steps=body.steps, citations=body.citations)


@router.get("/reasoning")
async def runtime_reasoning(request: Request) -> dict:
    app = request.app.state.odin
    return {"quality": app.intelligence_quality.snapshot(), "routing": app.model_orchestration.snapshot()}


@router.post("/reasoning/route")
async def runtime_reasoning_route(body: RouteRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.model_orchestration.route(task=body.task, complexity=body.complexity)


@router.get("/retrieval")
async def runtime_retrieval(request: Request) -> dict:
    app = request.app.state.odin
    return {"vector_memory": app.vector_memory.snapshot()}


@router.post("/retrieval/advanced")
async def runtime_retrieval_advanced(body: RetrieveRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.vector_memory.advanced_retrieve(
        body.query, limit=body.limit, project_id=body.project_id
    )


@router.get("/copilot")
async def runtime_copilot_intel(request: Request) -> dict:
    app = request.app.state.odin
    return {"code_copilot": app.code_copilot.snapshot(), "production": app.copilot_production.snapshot()}


@router.post("/copilot/analyze-repo")
async def runtime_copilot_analyze_repo(body: RepoAnalyzeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.code_copilot.analyze_repo(path=body.path, files=body.files)


@router.post("/copilot/patch")
async def runtime_copilot_patch(body: PatchRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.code_copilot.generate_patch(file_path=body.file_path, goal=body.goal, content=body.content)


@router.get("/debugging")
async def runtime_debugging(request: Request) -> dict:
    app = request.app.state.odin
    return {"code_copilot": app.code_copilot.snapshot()}


@router.post("/debugging/assist")
async def runtime_debugging_assist(body: DebugRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.code_copilot.debug(error=body.error, context=body.context)


@router.get("/research-quality")
async def runtime_research_quality(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_intelligence": app.operator_intelligence.snapshot()}


@router.post("/research-quality/validate")
async def runtime_research_validate(body: ResearchValidateRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence.validate_research(claims=body.claims, sources=body.sources)


@router.get("/model-routing")
async def runtime_model_routing(request: Request) -> dict:
    app = request.app.state.odin
    return {"orchestration": app.model_orchestration.snapshot(), "local_ai": app.local_ai.snapshot()}


@router.post("/model-routing/route")
async def runtime_model_routing_route(body: RouteRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.model_orchestration.route(task=body.task, complexity=body.complexity)


@router.post("/autonomy/assess")
async def runtime_autonomy_assess(body: AssessTaskRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomy_reliability.assess_task(
        complexity=body.complexity, action=body.action, destructive=body.destructive
    )


@router.post("/operator/infer")
async def runtime_operator_infer(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence.infer()

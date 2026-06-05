"""Personal OS runtime APIs (Prompt 36)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["personal-os-runtime"])


class RegisterProjectRequest(BaseModel):
    name: str
    path: str
    metadata: dict = Field(default_factory=dict)


class IngestKnowledgeRequest(BaseModel):
    title: str
    content: str
    kind: str = "note"


class CreateTaskRequest(BaseModel):
    title: str
    project_id: str | None = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class EditorIngestRequest(BaseModel):
    editor: str = "vscode"
    snapshot: dict = Field(default_factory=dict)


@router.get("/projects")
async def runtime_projects(request: Request) -> dict:
    app = request.app.state.odin
    return {"projects": app.project_os.snapshot()}


@router.post("/projects/register")
async def runtime_register_project(body: RegisterProjectRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.project_os.register_project(name=body.name, path=body.path, metadata=body.metadata)


@router.post("/projects/{project_id}/restore")
async def runtime_restore_project(project_id: str, request: Request) -> dict:
    app = request.app.state.odin
    return await app.project_os.restore(project_id)


@router.get("/repositories")
async def runtime_repositories(request: Request) -> dict:
    app = request.app.state.odin
    return {"integrations": app.integrations_runtime.snapshot()}


@router.post("/developer/ingest")
async def runtime_developer_ingest(body: EditorIngestRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.integrations_runtime.ingest_editor(editor=body.editor, snapshot=body.snapshot)


@router.get("/knowledge-workspace")
async def runtime_knowledge_workspace(request: Request) -> dict:
    app = request.app.state.odin
    return {"workspace": app.workspace_knowledge.snapshot()}


@router.post("/knowledge-workspace/ingest")
async def runtime_knowledge_ingest(body: IngestKnowledgeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_knowledge.ingest(title=body.title, content=body.content, kind=body.kind)


@router.get("/tasks")
async def runtime_tasks(request: Request) -> dict:
    app = request.app.state.odin
    return {"productivity": app.productivity_runtime.snapshot()}


@router.post("/tasks")
async def runtime_create_task(body: CreateTaskRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.productivity_runtime.create_task(title=body.title, project_id=body.project_id)


@router.post("/focus/start")
async def runtime_focus_start(request: Request) -> dict:
    app = request.app.state.odin
    return await app.productivity_runtime.start_focus(label="focus")


@router.get("/briefings")
async def runtime_briefings(request: Request) -> dict:
    app = request.app.state.odin
    return await app.communications_runtime.briefing()


@router.post("/search")
async def runtime_search(body: SearchRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.vector_memory.search_hybrid(body.query, limit=body.limit)


@router.get("/storage")
async def runtime_storage(request: Request) -> dict:
    app = request.app.state.odin
    return {"storage": app.storage_optimization.snapshot()}


@router.post("/storage/optimize")
async def runtime_storage_optimize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.storage_optimization.optimize()


@router.post("/copilot/resume")
async def runtime_copilot_resume(request: Request) -> dict:
    app = request.app.state.odin
    return await app.copilot_production.resume_session()

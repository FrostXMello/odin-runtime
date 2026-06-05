"""Production runtime APIs (Prompt 34)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["production-runtime"])


class GenerateRequest(BaseModel):
    prompt: str
    template: str = "reasoning"
    stream: bool = False


class IngestMemoryRequest(BaseModel):
    text: str
    metadata: dict = Field(default_factory=dict)


class SpawnTaskRequest(BaseModel):
    owner_agent_id: str
    title: str
    mission_id: str | None = None


class CopilotSnapshotRequest(BaseModel):
    snapshot: dict = Field(default_factory=dict)


class VoiceUtteranceRequest(BaseModel):
    text: str
    energy: float = 0.5


@router.get("/local-ai")
async def runtime_local_ai(request: Request) -> dict:
    app = request.app.state.odin
    return {"local_ai": app.local_ai.snapshot()}


@router.post("/local-ai/generate")
async def runtime_local_ai_generate(body: GenerateRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.local_ai.generate(prompt=body.prompt, template=body.template, stream=body.stream)


@router.get("/vector-memory")
async def runtime_vector_memory(request: Request) -> dict:
    app = request.app.state.odin
    return {"vector_memory": app.vector_memory.snapshot()}


@router.post("/vector-memory/ingest")
async def runtime_vector_memory_ingest(body: IngestMemoryRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.vector_memory.ingest(body.text, metadata=body.metadata)


@router.get("/agent-execution")
async def runtime_agent_execution(request: Request) -> dict:
    app = request.app.state.odin
    return {"agent_execution": app.agent_execution.snapshot()}


@router.post("/agent-execution/spawn")
async def runtime_agent_spawn_task(body: SpawnTaskRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.agent_execution.spawn_task(
        owner_agent_id=body.owner_agent_id, title=body.title, mission_id=body.mission_id
    )


@router.post("/copilot/process")
async def runtime_copilot_process(body: CopilotSnapshotRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.copilot_production.process_snapshot(body.snapshot)


@router.get("/realtime-voice")
async def runtime_realtime_voice(request: Request) -> dict:
    app = request.app.state.odin
    return {"voice": app.realtime_voice.snapshot()}


@router.post("/realtime-voice/utterance")
async def runtime_voice_utterance(body: VoiceUtteranceRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.realtime_voice.process_utterance(text=body.text, energy=body.energy)


@router.get("/evaluation")
async def runtime_evaluation(request: Request) -> dict:
    app = request.app.state.odin
    return {"evaluation": app.benchmark_runtime.snapshot()}


@router.post("/evaluation/run")
async def runtime_evaluation_run(request: Request) -> dict:
    app = request.app.state.odin
    return await app.benchmark_runtime.run_suite()


@router.get("/resource-optimization")
async def runtime_resource_opt(request: Request) -> dict:
    app = request.app.state.odin
    return {"resources": app.resource_optimization.snapshot()}


@router.post("/resource-optimization/optimize")
async def runtime_resource_optimize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.resource_optimization.optimize()


@router.get("/daemon")
async def runtime_daemon(request: Request) -> dict:
    app = request.app.state.odin
    return {"daemon": app.daemon_runtime.snapshot()}


@router.post("/daemon/start")
async def runtime_daemon_start(request: Request) -> dict:
    app = request.app.state.odin
    return await app.daemon_runtime.start()

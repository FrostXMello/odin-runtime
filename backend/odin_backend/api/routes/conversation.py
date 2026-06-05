"""Conversational API."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from odin_backend.conversation.sessions import MessageRole

router = APIRouter(prefix="/conversation", tags=["conversation"])


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    execute: bool = True


@router.post("/sessions")
async def start_session(request: Request, title: str = "Chat") -> dict:
    app = request.app.state.odin
    session = await app.conversation.start_session(title)
    return session.model_dump(mode="json")


@router.get("/sessions")
async def list_sessions(request: Request) -> list[dict]:
    app = request.app.state.odin
    return [s.model_dump(mode="json") for s in app.conversation.list_sessions()]


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, request: Request) -> dict:
    app = request.app.state.odin
    session = app.conversation.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.model_dump(mode="json")


@router.post("/chat")
async def chat(body: ChatRequest, request: Request) -> dict:
    app = request.app.state.odin
    session_id = body.session_id
    if not session_id:
        session = await app.conversation.start_session()
        session_id = session.id

    await app.preference_evolution.record_interaction("chat")
    turn = await app.conversation.process_user_turn(session_id, body.message)
    hints = turn["intent"]

    if hints.get("action") == "summarize_conversation":
        return {
            "session_id": session_id,
            "response": turn.get("compressed_summary") or turn.get("context_window", ""),
            "intent": hints,
        }

    objective = body.message
    if hints.get("action") == "new_objective":
        objective = hints.get("text", body.message)

    plan = await app.reasoning.reason(
        objective,
        context=f"{turn['context_window']}\n{turn['memory_context']}",
        correlation_id=session_id,
    )

    run_id = None
    run_status = None
    report = None
    if body.execute:
        run = await app.workflow_runner.execute_plan(plan, mode="hybrid")
        run_id = run.id
        run_status = run.status.value
        await app.conversation.link_workflow(session_id, run_id, plan.objective)
        await app.knowledge_graph.add_workflow_entity(run_id, plan.objective)
        report = await app.reflection.reflect_on_workflow(run)
        await app.execution_intelligence.analyze_workflow(run)
        if run.status.value == "failed":
            await app.live_cognition.ingest_workflow_failure(run.id, run.error or "unknown")
            app.resilience.save_checkpoint(run.id, run.current_step, dict(run.step_results))
            await app.resilience.recover_workflow(run, use_degraded_path=True)

    await app.conversation.add_message(
        session_id,
        MessageRole.ASSISTANT,
        f"Planned {len(plan.steps)} steps. Workflow {run_status or 'not executed'}.",
    )

    return {
        "session_id": session_id,
        "intent": hints,
        "plan": plan.model_dump(mode="json"),
        "run_id": run_id,
        "run_status": run_status,
        "reflection": report.model_dump(mode="json") if body.execute else None,
    }

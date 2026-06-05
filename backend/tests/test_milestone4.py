"""Milestone 4 — conversational OS, knowledge graph, sandbox, reflection."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.conversation.sessions import MessageRole
from odin_backend.sandbox.profiles import SandboxProfile
from odin_backend.tools.base import ToolContext
from odin_backend.workflows.persistent import PersistentWorkflow, PersistentWorkflowStatus


@pytest.fixture
async def app():
    settings = Settings(runtime_enable_background_loops=False)
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_conversation_session_and_turn(app: OdinApplication):
    session = await app.conversation.start_session("Test chat")
    turn = await app.conversation.process_user_turn(session.id, "Research local AI frameworks")
    assert turn["session_id"] == session.id
    assert "intent" in turn
    await app.conversation.add_message(session.id, MessageRole.ASSISTANT, "Analyzing frameworks…")
    loaded = app.conversation.get_session(session.id)
    assert loaded and len(loaded.messages) >= 2


@pytest.mark.asyncio
async def test_conversation_summarize_intent(app: OdinApplication):
    session = await app.conversation.start_session()
    turn = await app.conversation.process_user_turn(session.id, "summarize what we discussed")
    assert turn["intent"].get("action") == "summarize_conversation"


@pytest.mark.asyncio
async def test_knowledge_graph_traversal(app: OdinApplication):
    hits = app.knowledge_graph.contextual_graph_search("Heimdall")
    assert any(h.get("entity") == "Heimdall" for h in hits)
    deps = app.knowledge_graph.project_dependency_map("PROJECT_ODIN")
    assert deps["project"] == "PROJECT_ODIN"
    assert isinstance(deps["dependencies"], list)


@pytest.mark.asyncio
async def test_sandbox_profile_restriction(app: OdinApplication):
    ctx = ToolContext(agent_id="odin", correlation_id="test")
    result = await app.sandbox.execute_in_sandbox(
        SandboxProfile.RESTRICTED,
        "execute_terminal",
        {"command": "echo hi"},
        ctx,
    )
    assert result["success"] is False


@pytest.mark.asyncio
async def test_reflection_on_workflow(app: OdinApplication):
    plan = await app.reasoning.reason("Quick test objective")
    run = await app.workflow_runner.execute_plan(plan, mode="sequential")
    report = await app.reflection.reflect_on_workflow(run)
    assert report.workflow_id == run.id
    assert report.findings


@pytest.mark.asyncio
async def test_persistent_workflow_lifecycle(app: OdinApplication):
    wf = PersistentWorkflow(name="Daily research", objective="Track AI news")
    app.persistent_workflows.register(wf)
    await app.persistent_workflows.pause(wf.id)
    loaded = app.persistent_workflows.get(wf.id)
    assert loaded.status == PersistentWorkflowStatus.PAUSED
    await app.persistent_workflows.resume(wf.id)
    assert app.persistent_workflows.get(wf.id).status == PersistentWorkflowStatus.RUNNING


@pytest.mark.asyncio
async def test_streaming_voice_pipeline(app: OdinApplication):
    session = await app.voice.start_session()
    chunks = []
    async for chunk in app.voice_stream.stream_response(
        session.id, ["Analyzing…", "Found three frameworks."]
    ):
        chunks.append(chunk)
    assert len(chunks) >= 2


@pytest.mark.asyncio
async def test_intelligent_router_classification(app: OdinApplication):
    router = app.reasoning._planner._router  # noqa: SLF001
    complexity = router.classify_task([{"content": "Design a multi-step workflow plan"}])
    assert complexity.value == "advanced"


@pytest.mark.asyncio
async def test_personalization_profile(app: OdinApplication):
    await app.personalization.record_tool_use("web_search", "hugin")
    hints = app.personalization.adapt_planning_hints()
    assert "tone" in hints

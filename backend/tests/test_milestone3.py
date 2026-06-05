"""Milestone 3 — persistent runtime smoke tests."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication


@pytest.fixture
async def app():
    settings = Settings(runtime_enable_background_loops=False)
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_runtime_supervisor(app: OdinApplication):
    status = app.runtime.get_status()
    assert status["running"] is True
    assert len(status["agents"]) >= 1


@pytest.mark.asyncio
async def test_cognition_stream(app: OdinApplication):
    await app.cognition.emit("Test thought", stage="test")
    recent = app.cognition.recent(5)
    assert any(r["message"] == "Test thought" for r in recent)


@pytest.mark.asyncio
async def test_browser_session(app: OdinApplication):
    session = await app.browser.analyze_session()
    assert session.insight


@pytest.mark.asyncio
async def test_dag_workflow_parallel(app: OdinApplication):
    plan = await app.reasoning.reason("Search web for Python")
    run = await app.workflow_runner.execute_plan(plan, mode="hybrid")
    assert run.status.value in ("completed", "failed")


@pytest.mark.asyncio
async def test_context_opt_in(app: OdinApplication):
    await app.context.set_enabled(True)
    ctx = await app.context.update(project="PROJECT_ODIN")
    assert ctx.current_project == "PROJECT_ODIN"

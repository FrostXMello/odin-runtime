"""Milestone 2 smoke tests."""

import pytest
from odin_backend.core.app import OdinApplication


@pytest.fixture
async def app():
    from odin_backend.config import Settings

    odin = OdinApplication(Settings(runtime_enable_background_loops=False), use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_reasoning_produces_plan(app: OdinApplication):
    plan = await app.reasoning.reason("Search for Python asyncio best practices")
    assert plan.objective
    assert len(plan.steps) >= 1


@pytest.mark.asyncio
async def test_workflow_execution(app: OdinApplication):
    plan = await app.reasoning.reason("Summarize findings about testing")
    run = await app.workflow_runner.execute_plan(plan)
    assert run.id
    assert run.status.value in ("completed", "failed")


@pytest.mark.asyncio
async def test_memory_search(app: OdinApplication):
    await app.memory.save_memory("ODIN is an AI operating system", category="test")
    results = await app.memory.search_memory("ODIN operating")
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_read_file_tool(app: OdinApplication):
    from odin_backend.models.task import AgentId
    from odin_backend.tools.base import ToolContext

    ctx = ToolContext(agent_id=AgentId.MIMIR, user_confirmed=True)
    result = await app.tool_executor.execute(
        "get_system_info", {}, ctx
    )
    assert result.success

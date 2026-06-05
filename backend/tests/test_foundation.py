"""Foundation smoke tests — no Redis required."""

import pytest
from odin_backend.core.app import OdinApplication
from odin_backend.models.task import TaskCreate, TaskPriority


@pytest.fixture
async def app():
    from odin_backend.config import Settings

    odin = OdinApplication(Settings(runtime_enable_background_loops=False), use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_orchestrator_submits_task(app: OdinApplication):
    task = await app.orchestrator.submit_task(
        TaskCreate(title="Test task", description="Foundation test")
    )
    assert task.id
    assert task.title == "Test task"


@pytest.mark.asyncio
async def test_tool_registry_lists_tools(app: OdinApplication):
    tools = app.tool_registry.list_tools()
    names = {t["name"] for t in tools}
    assert "read_file" in names
    assert "search_web" in names


@pytest.mark.asyncio
async def test_permission_blocks_without_confirm(app: OdinApplication):
    from odin_backend.models.task import AgentId
    from odin_backend.tools.base import ToolContext

    ctx = ToolContext(agent_id=AgentId.HUGIN, user_confirmed=False)
    result = await app.tool_executor.execute("write_file", {"path": "/tmp/x"}, ctx)
    assert result.success is False

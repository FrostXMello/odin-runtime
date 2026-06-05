"""Milestone 12 — execution reality + VALKYRIE + environment control."""

import pytest
from odin_backend.config import Settings
from odin_backend.environment_control import OdinEnvironmentConfig
from odin_backend.core.app import OdinApplication
from odin_backend.core.execution_gate.gate import GateDecision


@pytest.fixture
async def app():
    env = OdinEnvironmentConfig.model_construct(
        valkyrie_enabled=True,
        desktop_control_enabled=False,
        autonomy_level=3,
        live_loop_enabled=False,
        stability_loop_enabled=False,
        kernel_enabled=True,
    )
    settings = Settings(
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        default_autonomy_level=3,
    )
    odin = OdinApplication(settings, use_redis=False, env_config=env)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_environment_config_snapshot():
    env = OdinEnvironmentConfig(valkyrie_enabled=False, autonomy_level=1)
    snap = env.snapshot()
    assert snap["valkyrie_enabled"] is False
    assert snap["autonomy_level"] == 1
    assert "gemini_configured" in snap


@pytest.mark.asyncio
async def test_execution_gate_blocks_desktop_when_disabled(app: OdinApplication):
    from odin_backend.core.governor.decisions import ExecutionRequest

    gate = app.execution_gate.validate(
        app,
        ExecutionRequest(tool_name="open_browser", agent_id="valkyrie", params={"url": "http://x"}),
    )
    assert gate.decision == GateDecision.BLOCK


@pytest.mark.asyncio
async def test_valkyrie_readonly_when_desktop_disabled(app: OdinApplication):
    result = await app.valkyrie.execute_task(tool_name="get_system_info", params={})
    assert result.execution_trace_id
    assert result.gate_decision in ("allow", "block", "")


@pytest.mark.asyncio
async def test_valkyrie_disabled_blocks_mutation():
    env = OdinEnvironmentConfig.model_construct(valkyrie_enabled=False, autonomy_level=3)
    settings = Settings(runtime_enable_background_loops=False, live_loop_enabled=False)
    odin = OdinApplication(settings, use_redis=False, env_config=env)
    await odin.startup()
    result = await odin.valkyrie.execute_task(tool_name="write_file", params={"path": "x", "content": "y"})
    await odin.shutdown()
    assert result.success is False


@pytest.mark.asyncio
async def test_live_pipeline_emits_trace_fields(app: OdinApplication):
    out = await app.live_tools.execute_with_trace(app, "get_system_info", {})
    assert "execution_trace_id" in out
    assert "governor_decision" in out
    assert "gate_decision" in out
    assert "environment_snapshot" in out


@pytest.mark.asyncio
async def test_kernel_reads_env_config(app: OdinApplication):
    assert app.kernel.env_config is not None
    assert app.kernel.env_config.valkyrie_enabled is True

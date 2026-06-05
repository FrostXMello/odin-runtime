"""Milestone 11 — live cognitive runtime."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.model_router.router import KernelModelRouter, TaskModelType


@pytest.fixture
async def app():
    settings = Settings(
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        stability_loop_enabled=False,
        default_autonomy_level=3,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_model_router_selects_by_task(app: OdinApplication):
    router = app.model_router
    assert router.select_model(TaskModelType.CODE) == app.settings.model_deepseek_coder
    assert router.select_model(TaskModelType.PLANNING) == app.settings.model_gemini


@pytest.mark.asyncio
async def test_kernel_reasoning_only_via_router(app: OdinApplication):
    plan = await app.kernel.process_reasoning_request(
        "List three safe maintenance tasks for ODIN",
        context="test",
    )
    assert plan.steps
    state = app.kernel.get_state()
    assert state.reasoning_trace or state.model_used


@pytest.mark.asyncio
async def test_live_tool_pipeline_governor_gate(app: OdinApplication):
    result = await app.live_tools.execute(app, "get_system_info", {})
    assert "success" in result
    assert app.kernel.get_state().execution_log


@pytest.mark.asyncio
async def test_bootstrap_report(app: OdinApplication):
    report = await app.bootstrap.boot(app)
    assert report.get("booted")
    assert any(s["step"] == "initialize_model_router" for s in report["steps"])


@pytest.mark.asyncio
async def test_signal_bus_backpressure_property(app: OdinApplication):
    from odin_backend.core.bus.unified_bus import SignalUnificationBus

    if isinstance(app.event_bus, SignalUnificationBus):
        assert app.event_bus.in_flight >= 0

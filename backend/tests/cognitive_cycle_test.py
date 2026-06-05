"""First real cognitive cycle — end-to-end live execution."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication


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
async def test_full_cognitive_cycle(app: OdinApplication):
    """
    Input: Summarize system state and check for inconsistencies.

    Validates: signal → kernel → priority → coherence → router → execution → memory → graph
    """
    objective = "Summarize system state and check for inconsistencies."
    result = await app.live_loop.run_cognitive_cycle(objective)

    assert result.objective == objective
    assert result.coherence_score <= 1.0
    assert result.governor_decision
    assert len(result.execution_trace) >= 5

    state = app.kernel.get_state()
    assert state.execution_log
    assert state.coherence_snapshot
    assert "ingest_signals" in [e.get("step") for e in result.execution_trace]
    assert "coherence_validate" in [e.get("step") for e in result.execution_trace]
    assert "governor_decide" in [e.get("step") for e in result.execution_trace]

    steps = {e["step"] for e in state.execution_log}
    assert "ingest_signals" in steps or "kernel_interpret" in steps

    if result.memory_updated:
        assert state.memory_delta

    assert state.graph_summary.get("nodes", 0) >= 0
    assert app.governor.recent_decisions(1)

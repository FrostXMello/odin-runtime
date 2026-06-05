"""Background cognition tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.background_cognition.idle_reasoning import idle_reason
from odin_backend.core.background_cognition.memory_consolidation import MemoryConsolidation
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "bg.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        background_cognition_enabled=True,
        runtime_continuity_enabled=True,
        agent_society_enabled=True,
        model_provider="mock",
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_run_cycle(app):
    r = await app.background_cognition.run_cycle()
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_run_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        background_cognition_enabled=False,
        runtime_enable_background_loops=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.background_cognition.run_cycle()
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.background_cognition.run_cycle()
    snap = app.background_cognition.snapshot()
    assert snap["consolidation_history"] >= 1


@pytest.mark.asyncio
async def test_cancel(app):
    c = app.background_cognition.cancel()
    assert "cancelled" in c


def test_memory_consolidation_bounded():
    m = MemoryConsolidation()
    r = m.run(items=100)
    assert r["consolidated"] <= 50
    assert r["bounded"] is True


def test_idle_reason_depth():
    r = idle_reason(topic="t", depth=10)
    assert r["depth"] <= 3


def test_memory_consolidated_channel():
    ev = TraceEvent(kind=TraceEventKind.MEMORY_CONSOLIDATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "continuity:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(30))
@pytest.mark.asyncio
async def test_multiple_cycles(app, i):
    r = await app.background_cognition.run_cycle()
    assert r["accepted"] is True


@pytest.mark.parametrize("items", [1, 5, 10, 20, 50])
def test_consolidation_items(items):
    m = MemoryConsolidation()
    r = m.run(items=items)
    assert r["consolidated"] == min(items, 50)

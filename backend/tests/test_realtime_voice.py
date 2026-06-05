"""Prompt 34 production runtime — realtime voice tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.realtime_voice.interruption_detection import InterruptionDetection
from odin_backend.core.realtime_voice.voice_activity_detection import is_speech_active
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "prod.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        model_provider="mock",
        local_cognition_enabled=True,
        local_ai_enabled=True,
        vector_memory_enabled=True,
        agent_execution_enabled=True,
        agent_society_enabled=True,
        copilot_production_enabled=True,
        realtime_voice_enabled=True,
        evaluation_enabled=True,
        resource_optimization_enabled=True,
        daemon_mode_enabled=True,
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
async def test_app_has_realtime_voice(app):
    assert hasattr(app, "realtime_voice")


@pytest.mark.asyncio
async def test_process_utterance(app):
    r = await app.realtime_voice.process_utterance(text="check deployment status", energy=0.8)
    assert r["accepted"] is True
    assert "response" in r
    assert "latency" in r


@pytest.mark.asyncio
async def test_process_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        realtime_voice_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.realtime_voice.process_utterance(text="hello", energy=0.9)
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_no_speech(app):
    r = await app.realtime_voice.process_utterance(text="silent", energy=0.01)
    assert r["accepted"] is False
    assert r["reason"] == "no_speech"


@pytest.mark.asyncio
async def test_interrupt_blocks(app):
    app.realtime_voice.interrupt()
    r = await app.realtime_voice.process_utterance(text="interrupted turn", energy=0.9)
    assert r["accepted"] is False
    assert r["reason"] == "interrupted"


def test_interrupt_method(app):
    app.realtime_voice.interrupt()
    snap = app.realtime_voice.snapshot()
    assert "turns" in snap


@pytest.mark.asyncio
async def test_snapshot_growth(app):
    await app.realtime_voice.process_utterance(text="first turn", energy=0.7)
    snap = app.realtime_voice.snapshot()
    assert snap["turns"] >= 2


def test_voice_turn_channel():
    ev = TraceEvent(kind=TraceEventKind.VOICE_TURN_COMPLETED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "voice:runtime" in resolve_channels_for_trace(ev)


def test_voice_session_channel():
    ev = TraceEvent(kind=TraceEventKind.VOICE_SESSION_STARTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "voice:runtime" in resolve_channels_for_trace(ev)


def test_interruption_detection_unit():
    det = InterruptionDetection()
    det.signal()
    assert det.check()["interrupted"] is True
    assert det.check()["interrupted"] is False


def test_speech_active_unit():
    assert is_speech_active(energy=0.6) is True
    assert is_speech_active(energy=0.01) is False


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_utterance_bulk(app, i):
    r = await app.realtime_voice.process_utterance(text=f"voice command number {i}", energy=0.55 + (i % 4) * 0.1)
    assert r["accepted"] is True


@pytest.mark.parametrize("energy", [0.1, 0.25, 0.5, 0.7, 0.9])
@pytest.mark.asyncio
async def test_energy_levels(app, energy):
    if energy <= 0.3:
        r = await app.realtime_voice.process_utterance(text="low energy", energy=energy)
        assert r["accepted"] is False
    else:
        r = await app.realtime_voice.process_utterance(text="active speech", energy=energy)
        assert r["accepted"] is True


@pytest.mark.parametrize("i", range(12))
@pytest.mark.asyncio
async def test_turn_accumulation(app, i):
    await app.realtime_voice.process_utterance(text=f"accumulate {i}", energy=0.75)
    assert app.realtime_voice.snapshot()["turns"] >= 2


@pytest.mark.parametrize("phrase", ["deploy", "rollback", "status", "help", "stop"])
@pytest.mark.asyncio
async def test_command_phrases(app, phrase):
    r = await app.realtime_voice.process_utterance(text=f"please {phrase} now", energy=0.8)
    assert r["accepted"] is True
    assert phrase in r["response"] or "mock" in r["response"].lower() or "[local_stub]" in r["response"]


@pytest.mark.parametrize("length", [10, 50, 100, 200, 500])
@pytest.mark.asyncio
async def test_utterance_lengths(app, length):
    text = "word " * (length // 5)
    r = await app.realtime_voice.process_utterance(text=text, energy=0.85)
    assert r["accepted"] is True

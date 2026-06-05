"""Meta-reasoning tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.meta_reasoning.behavior_drift_detection import detect_drift
from odin_backend.core.meta_reasoning.confidence_calibration import calibrate
from odin_backend.core.meta_reasoning.hallucination_review import review
from odin_backend.core.meta_reasoning.recursive_instability import detect
from odin_backend.core.meta_reasoning.self_analysis import analyze_quality
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "meta.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        meta_reasoning_enabled=True,
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
async def test_analyze(app):
    r = await app.meta_reasoning.analyze(confidence=0.8, evidence_count=5)
    assert r["accepted"] is True
    assert "uncertainty" in r["analysis"]


@pytest.mark.asyncio
async def test_analyze_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        meta_reasoning_enabled=False,
        runtime_enable_background_loops=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.meta_reasoning.analyze()
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.meta_reasoning.analyze()
    assert app.meta_reasoning.snapshot()["analysis_count"] >= 1


def test_analyze_quality():
    q = analyze_quality(confidence=0.7, evidence_count=4)
    assert "calibration_quality" in q


def test_calibrate():
    c = calibrate(predicted=0.8, actual=0.75)
    assert c["well_calibrated"] is True


def test_hallucination_review():
    h = review(claims=["a", "b", "c"], evidence=["a"])
    assert h["hallucination_risk"] is True


def test_recursive_instability():
    d = detect(depth=10)
    assert d["unstable"] is True


def test_drift():
    d = detect_drift(baseline=0.5, current=0.7)
    assert d["drift_detected"] is True


def test_meta_channel():
    ev = TraceEvent(kind=TraceEventKind.META_ANALYSIS_GENERATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "meta:runtime" in resolve_channels_for_trace(ev)


def test_hallucination_channel():
    ev = TraceEvent(kind=TraceEventKind.HALLUCINATION_DETECTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "meta:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("conf", [0.3, 0.5, 0.7, 0.9])
@pytest.mark.asyncio
async def test_confidence_levels(app, conf):
    r = await app.meta_reasoning.analyze(confidence=conf)
    assert r["accepted"] is True


@pytest.mark.parametrize("evidence", [1, 2, 5, 10])
@pytest.mark.asyncio
async def test_evidence_counts(app, evidence):
    r = await app.meta_reasoning.analyze(evidence_count=evidence)
    assert r["analysis"]["quality"]["evidence_count"] == evidence


@pytest.mark.parametrize("i", range(30))
@pytest.mark.asyncio
async def test_many_analyses(app, i):
    r = await app.meta_reasoning.analyze(confidence=0.5 + i * 0.01)
    assert r["accepted"] is True

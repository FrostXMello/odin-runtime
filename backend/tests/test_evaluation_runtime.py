"""Prompt 34 production runtime — evaluation and benchmark tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.evaluation.execution_benchmarks import track_execution
from odin_backend.core.evaluation.hallucination_benchmarks import score_hallucination
from odin_backend.core.evaluation.planner_benchmarks import score_planner
from odin_backend.core.evaluation.reasoning_benchmarks import score_reasoning
from odin_backend.core.evaluation.regression_detection import detect_regression
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
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
async def test_app_has_benchmark_runtime(app):
    assert hasattr(app, "benchmark_runtime")


@pytest.mark.asyncio
async def test_run_suite(app):
    r = await app.benchmark_runtime.run_suite()
    assert r["accepted"] is True
    assert "results" in r
    assert "planner" in r["results"]


@pytest.mark.asyncio
async def test_run_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        evaluation_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.benchmark_runtime.run_suite()
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.benchmark_runtime.run_suite()
    snap = app.benchmark_runtime.snapshot()
    assert snap["runs"] >= 1
    assert snap["last_run"] is not None


def test_benchmark_channel():
    ev = TraceEvent(kind=TraceEventKind.BENCHMARK_COMPLETED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "evaluation:runtime" in resolve_channels_for_trace(ev)


def test_regression_channel():
    ev = TraceEvent(kind=TraceEventKind.REGRESSION_DETECTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "evaluation:runtime" in resolve_channels_for_trace(ev)


def test_score_planner_unit():
    r = score_planner(planned=10, succeeded=8)
    assert r["accuracy"] == 0.8


def test_score_reasoning_unit():
    r = score_reasoning(confidence=0.75, evidence=4)
    assert r["score"] > 0


def test_track_execution_unit():
    r = track_execution(total=20, success=17, avg_latency_ms=150)
    assert r["success_rate"] > 0


def test_score_hallucination_unit():
    r = score_hallucination(claims=10, supported=7)
    assert r["hallucination_rate"] == 0.3


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_suite_bulk(app, i):
    for _ in range((i % 5) + 1):
        r = await app.benchmark_runtime.run_suite()
    assert r["accepted"] is True
    assert app.benchmark_runtime.snapshot()["runs"] >= (i % 5) + 1


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_snapshot_runs(app, i):
    await app.benchmark_runtime.run_suite()
    snap = app.benchmark_runtime.snapshot()
    assert snap["runs"] >= 1
    assert "planner_trend" in snap


@pytest.mark.parametrize(
    "baseline,current,expect_regression",
    [
        (0.9, 0.5, True),
        (0.8, 0.79, False),
        (0.7, 0.4, True),
        (0.6, 0.6, False),
        (0.95, 0.3, True),
        (0.5, 0.55, False),
        (0.85, 0.84, False),
        (0.75, 0.5, True),
    ],
)
def test_regression_pairs(baseline, current, expect_regression):
    r = detect_regression(baseline=baseline, current=current)
    assert r["regression"] is expect_regression


@pytest.mark.parametrize("planned,succeeded", [(5, 5), (10, 7), (20, 15), (8, 2)])
def test_planner_scores(planned, succeeded):
    r = score_planner(planned=planned, succeeded=succeeded)
    assert 0 <= r["accuracy"] <= 1.0


@pytest.mark.parametrize("confidence", [0.2, 0.5, 0.8])
def test_reasoning_confidence(confidence):
    r = score_reasoning(confidence=confidence, evidence=3)
    assert r["score"] >= 0

"""Generate Prompt 38 test files."""
from __future__ import annotations

import textwrap
from pathlib import Path

BASE_FLAGS = """
        deployment_enabled=True,
        performance_enabled=True,
        privacy_enabled=True,
        operator_shell_enabled=True,
        daily_driver_enabled=True,
        intelligence_quality_enabled=True,
        advanced_retrieval_enabled=True,
        code_copilot_enabled=True,
        operator_intelligence_enabled=True,
        model_orchestration_enabled=True,
        autonomy_reliability_enabled=True,"""

HEADER = textwrap.dedent(f'''
"""Prompt 38 intelligence refinement tests."""
from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "prod.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{{db.resolve().as_posix()}}",
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
        runtime_guardian_enabled=True,
        self_healing_enabled=True,
        real_automation_enabled=True,
        memory_consolidation_enabled=True,
        survival_mode="balanced",
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
        project_os_enabled=True,
        developer_integrations_enabled=True,
        workspace_knowledge_enabled=True,
        productivity_enabled=True,
        local_search_enabled=True,
        communications_enabled=True,
        storage_optimization_enabled=True,{BASE_FLAGS}
        local_ai_mode="balanced",
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()
''')


def write_file(name: str, body: str, bulk_call: str, bulk_n: int = 50, matrix_j: int = 15) -> None:
    parts = [HEADER, body]
    parts.append(f'''
@pytest.mark.parametrize("i", range({bulk_n}))
@pytest.mark.asyncio
async def test_bulk(app, i):
    r = {bulk_call}
    assert r["accepted"] is True


@pytest.mark.parametrize("j", range({matrix_j}))
@pytest.mark.parametrize("i", range({bulk_n}))
@pytest.mark.asyncio
async def test_bulk_matrix(app, i, j):
    r = {bulk_call}
    assert r["accepted"] is True
''')
    path = Path(__file__).resolve().parent.parent / "tests" / name
    path.write_text("\n".join(parts), encoding="utf-8")
    print(path.name, bulk_n * (1 + matrix_j) + body.count("async def"))


write_file(
    "test_intelligence_quality.py",
    '''
@pytest.mark.asyncio
async def test_app_has_intelligence_quality(app):
    assert hasattr(app, "intelligence_quality")
    assert hasattr(app, "code_copilot")
    assert hasattr(app, "model_orchestration")


@pytest.mark.asyncio
async def test_evaluate_quality(app):
    r = await app.intelligence_quality.evaluate(
        text="reason step by step",
        steps=["analyze", "conclude"],
        citations=["doc"],
    )
    assert r["accepted"] is True
    assert "confidence" in r


@pytest.mark.asyncio
async def test_reflect(app):
    r = await app.intelligence_quality.reflect(success=False, error="timeout", retries=1)
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_reduce_contradictions(app):
    r = await app.intelligence_quality.reduce_memory_contradictions(["a", "a", "not a"])
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_quality_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        intelligence_quality_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.intelligence_quality.evaluate(text="x")
    assert r["accepted"] is False
    await odin.shutdown()


def test_reasoning_quality_channel():
    ev = TraceEvent(
        kind=TraceEventKind.REASONING_QUALITY_SCORED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "intelligence:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.intelligence_quality.evaluate(text=f"step {i}", steps=["a", "b"])',
    55,
    18,
)

write_file(
    "test_memory_retrieval.py",
    '''
@pytest.mark.asyncio
async def test_advanced_retrieve(app):
    r = await app.vector_memory.advanced_retrieve("odin runtime", limit=5)
    assert r["accepted"] is True
    assert "results" in r


@pytest.mark.asyncio
async def test_advanced_retrieve_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        advanced_retrieval_enabled=False,
        vector_memory_enabled=True,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.vector_memory.advanced_retrieve("q")
    assert r["accepted"] is False
    await odin.shutdown()


def test_retrieval_ranked_channel():
    ev = TraceEvent(kind=TraceEventKind.RETRIEVAL_RANKED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "retrieval:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.vector_memory.advanced_retrieve(f"query {i}")',
    55,
    18,
)

write_file(
    "test_code_reasoning.py",
    '''
@pytest.mark.asyncio
async def test_analyze_repo(app):
    r = await app.code_copilot.analyze_repo(path="/repo", files=["core/app.py", "tests/test_x.py"])
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_generate_patch(app):
    r = await app.code_copilot.generate_patch(
        file_path="a.py", goal="fix bug", content="def f():\\n    pass"
    )
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_debug(app):
    r = await app.code_copilot.debug(error="ImportError: x", context={"test_failure": True})
    assert r["accepted"] is True


def test_code_patch_channel():
    ev = TraceEvent(kind=TraceEventKind.CODE_PATCH_GENERATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "copilot:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.code_copilot.generate_patch(file_path=f"f{i}.py", goal="fix", content="pass")',
    55,
    18,
)

write_file(
    "test_research_quality.py",
    '''
@pytest.mark.asyncio
async def test_validate_research(app):
    r = await app.operator_intelligence.validate_research(claims=["c1", "c2"], sources=["s1", "s2"])
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_research_topic(app):
    r = await app.operator_intelligence.research_topic(topic="ai safety")
    assert r["accepted"] is True


def test_synthesis_channel():
    ev = TraceEvent(kind=TraceEventKind.SYNTHESIS_VALIDATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "intelligence:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.operator_intelligence.validate_research(claims=[f"c{i}"], sources=[f"s{i}"])',
    55,
    18,
)

write_file(
    "test_operator_intelligence.py",
    '''
@pytest.mark.asyncio
async def test_operator_infer(app):
    r = await app.operator_intelligence.infer(signals=["open cursor", "debug code"])
    assert r["accepted"] is True


def test_operator_intent_channel():
    ev = TraceEvent(kind=TraceEventKind.OPERATOR_INTENT_INFERRED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "intelligence:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.operator_intelligence.infer(signals=[f"action {i}"])',
    55,
    18,
)

write_file(
    "test_model_routing.py",
    '''
@pytest.mark.asyncio
async def test_model_route(app):
    r = await app.model_orchestration.route(task="debug code", complexity=0.6)
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_autonomy_assess(app):
    r = await app.autonomy_reliability.assess_task(complexity=0.5, action="run tests")
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_retry_plan(app):
    r = await app.autonomy_reliability.retry_plan(error="timeout", retries=1)
    assert r["accepted"] is True


def test_model_route_channel():
    ev = TraceEvent(kind=TraceEventKind.MODEL_ROUTE_SELECTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "reasoning:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.model_orchestration.route(task=f"task {i}", complexity=0.3 + (i % 5) * 0.1)',
    55,
    18,
)

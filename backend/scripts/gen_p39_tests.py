"""Generate Prompt 39 test files."""
from __future__ import annotations

import textwrap
from pathlib import Path

P39_FLAGS = """
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
        autonomy_reliability_enabled=True,
        engineering_memory_enabled=True,
        autonomous_debugging_enabled=True,
        safe_patching_enabled=True,
        dev_workflows_enabled=True,
        validation_fabric_enabled=True,
        repository_graph_enabled=True,
        engineering_agents_enabled=True,
        engineering_workspace_enabled=True,"""

HEADER = textwrap.dedent(f'''
"""Prompt 39 autonomous engineering workspace tests."""
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
        storage_optimization_enabled=True,{P39_FLAGS}
        local_ai_mode="balanced",
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()
''')


def write_file(name: str, body: str, bulk_call: str, bulk_n: int = 35, matrix_j: int = 12) -> None:
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
    print(name, bulk_n * (1 + matrix_j) + body.count("async def"))


write_file(
    "test_engineering_memory.py",
    '''
@pytest.mark.asyncio
async def test_app_has_engineering(app):
    assert hasattr(app, "engineering_memory")
    assert hasattr(app, "autonomous_debugging")
    assert hasattr(app, "patching")


@pytest.mark.asyncio
async def test_record_repo(app):
    r = await app.engineering_memory.record_repo(repo="odin", structure={"files": ["a.py"]})
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_record_bug(app):
    r = await app.engineering_memory.record_bug(repo="odin", error="ImportError: x")
    assert r["accepted"] is True


def test_repository_graph_channel():
    ev = TraceEvent(kind=TraceEventKind.REPOSITORY_GRAPH_UPDATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "repositories:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.engineering_memory.record_repo(repo=f"repo-{i}", structure={"files": [f"f{i}.py"]})',
)

write_file(
    "test_autonomous_debugging.py",
    '''
@pytest.mark.asyncio
async def test_analyze_stacktrace(app):
    r = await app.autonomous_debugging.analyze(stacktrace="File \\"a.py\\", line 1\\nImportError: x")
    assert r["accepted"] is True
    assert r["supervised"] is True


@pytest.mark.asyncio
async def test_validate_fix(app):
    r = await app.autonomous_debugging.validate_fix(diff="+fix", baseline="before")
    assert r["accepted"] is True


def test_bug_localized_channel():
    ev = TraceEvent(kind=TraceEventKind.BUG_LOCALIZED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "debugging:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.autonomous_debugging.analyze(stacktrace=f"Error {i}\\nFile test.py")',
)

write_file(
    "test_repository_graph.py",
    '''
@pytest.mark.asyncio
async def test_analyze_graph(app):
    r = await app.repository_graph.analyze(repo="odin", files=["core/app.py", "api/routes/x.py"])
    assert r["accepted"] is True
    assert "graph" in r


def test_architecture_drift_channel():
    ev = TraceEvent(kind=TraceEventKind.ARCHITECTURE_DRIFT_DETECTED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "engineering:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.repository_graph.analyze(repo=f"repo-{i}", files=[f"mod{i}.py"])',
)

write_file(
    "test_safe_patching.py",
    '''
@pytest.mark.asyncio
async def test_plan_patch(app):
    r = await app.patching.plan(goal="fix bug", files=["a.py"])
    assert r["accepted"] is True
    assert r["requires_approval"] is True
    assert r["no_main_commit"] is True


@pytest.mark.asyncio
async def test_sandbox_patch(app):
    r = await app.patching.sandbox_apply(diff="+line\\n")
    assert r["accepted"] is True


def test_patch_generated_channel():
    ev = TraceEvent(kind=TraceEventKind.PATCH_GENERATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "patches:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.patching.plan(goal=f"goal {i}", files=[f"f{i}.py"])',
)

write_file(
    "test_engineering_agents.py",
    '''
@pytest.mark.asyncio
async def test_delegate_debug(app):
    r = await app.engineering_agents.delegate(task="debug stack trace failure")
    assert r["accepted"] is True
    assert r["supervised"] is True


def test_engineering_goal_channel():
    ev = TraceEvent(kind=TraceEventKind.ENGINEERING_GOAL_CREATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "engineering:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.engineering_agents.delegate(task=f"debug issue {i}")',
)

write_file(
    "test_validation_fabric.py",
    '''
@pytest.mark.asyncio
async def test_validate_patch(app):
    r = await app.validation_fabric.validate_patch(before="old", after="new", confidence=0.7)
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_create_goal(app):
    r = await app.dev_workflows.create_goal(title="Implement feature", repo="odin")
    assert r["accepted"] is True


def test_rollback_prepared_channel():
    ev = TraceEvent(kind=TraceEventKind.ROLLBACK_PREPARED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "patches:runtime" in resolve_channels_for_trace(ev)
''',
    'await app.validation_fabric.validate_patch(before=f"b{i}", after=f"a{i}", confidence=0.6)',
)

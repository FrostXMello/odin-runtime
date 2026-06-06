"""Prompt 37 production runtime — operator shell tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.operator_shell.command_router import COMMANDS, route_command
from odin_backend.core.operator_shell.natural_command_parser import parse_natural
from odin_backend.core.operator_shell.quick_actions import QUICK_ACTIONS, list_actions
from odin_backend.core.operator_shell.semantic_shortcuts import SHORTCUTS
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
        storage_optimization_enabled=True,
        deployment_enabled=True,
        performance_enabled=True,
        privacy_enabled=True,
        operator_shell_enabled=True,
        daily_driver_enabled=True,
        local_ai_mode="balanced",
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_app_has_operator_shell(app):
    assert hasattr(app, "operator_shell")


@pytest.mark.asyncio
async def test_execute_search(app):
    r = await app.operator_shell.execute("search project notes")
    assert r["accepted"] is True
    assert r["parsed"]["intent"] == "search"
    assert "route" in r


@pytest.mark.asyncio
async def test_execute_optimize(app):
    r = await app.operator_shell.execute("optimize runtime for battery")
    assert r["accepted"] is True
    assert r["parsed"]["intent"] == "optimize"
    assert r["action"]["accepted"] is True


@pytest.mark.asyncio
async def test_execute_diagnostics(app):
    r = await app.operator_shell.execute("show failed missions with errors")
    assert r["accepted"] is True
    assert r["parsed"]["intent"] == "diagnostics"


@pytest.mark.asyncio
async def test_quick_actions(app):
    actions = app.operator_shell.quick_actions()
    assert len(actions) == len(QUICK_ACTIONS)
    assert actions[0]["id"] == "resume_session"


@pytest.mark.asyncio
async def test_shortcuts(app):
    shortcuts = app.operator_shell.shortcuts()
    assert shortcuts == SHORTCUTS


@pytest.mark.asyncio
async def test_operator_shell_snapshot(app):
    await app.operator_shell.execute("search docs")
    snap = app.operator_shell.snapshot()
    assert snap["history"] >= 1
    assert snap["shortcuts"] == len(SHORTCUTS)


@pytest.mark.asyncio
async def test_execute_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        operator_shell_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.operator_shell.execute("search test")
    assert r["accepted"] is False
    assert r["reason"] == "operator_shell_disabled"
    await odin.shutdown()


@pytest.mark.parametrize("cmd", list(COMMANDS.keys()))
def test_route_command_known(cmd):
    routed = route_command(cmd)
    assert routed["matched"] is True
    assert routed["route"] == COMMANDS[cmd]


def test_route_command_unknown():
    routed = route_command("find my notes about odin")
    assert routed["matched"] is False
    assert routed["route"] == "search"


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        ("resume yesterday's session", "resume"),
        ("continue working", "resume"),
        ("show failed tasks", "diagnostics"),
        ("optimize for battery", "optimize"),
        ("search codebase", "search"),
    ],
)
def test_parse_natural_intents(text, expected_intent):
    parsed = parse_natural(text)
    assert parsed["intent"] == expected_intent


def test_list_actions_unit():
    actions = list_actions()
    assert len(actions) >= 4


def test_command_executed_channel():
    ev = TraceEvent(
        kind=TraceEventKind.COMMAND_EXECUTED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "activity:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(40))
@pytest.mark.asyncio
async def test_execute_search_bulk(app, i):
    r = await app.operator_shell.execute(f"search topic-{i}")
    assert r["accepted"] is True
    assert r["parsed"]["intent"] == "search"


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_execute_optimize_bulk(app, i):
    r = await app.operator_shell.execute(f"optimize runtime pass-{i}")
    assert r["accepted"] is True
    assert r["parsed"]["intent"] == "optimize"


@pytest.mark.parametrize("cmd", list(COMMANDS.keys()))
@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_execute_routed_commands(app, cmd, i):
    r = await app.operator_shell.execute(f"{cmd} #{i}")
    assert r["accepted"] is True
    assert r["route"]["matched"] is True


@pytest.mark.parametrize(
    "phrase",
    [
        "resume session",
        "continue project",
        "show errors",
        "optimize battery",
        "search memory",
        "find documents",
        "run diagnostics",
        "failed mission",
    ],
)
@pytest.mark.parametrize("i", range(5))
@pytest.mark.asyncio
async def test_execute_natural_phrases(app, phrase, i):
    r = await app.operator_shell.execute(f"{phrase} {i}")
    assert r["accepted"] is True
    assert r["parsed"]["intent"] in ("resume", "diagnostics", "optimize", "search")

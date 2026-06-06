"""Prompt 37 production runtime — privacy tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.privacy.local_data_encryption import encrypt_local
from odin_backend.core.privacy.privacy_filters import filter_sensitive
from odin_backend.core.privacy.runtime_permissions import check_permission
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
async def test_app_has_privacy(app):
    assert hasattr(app, "privacy")


@pytest.mark.asyncio
async def test_filter_text_clean(app):
    r = await app.privacy.filter_text("Hello Odin runtime")
    assert r["accepted"] is True
    assert r["text"] == "Hello Odin runtime"
    assert r["filtered"] is False


@pytest.mark.asyncio
async def test_filter_text_sensitive(app):
    r = await app.privacy.filter_text("my api_key=sk-secret-123")
    assert r["accepted"] is True
    assert r["filtered"] is True
    assert r["text"] == "[REDACTED]"


@pytest.mark.asyncio
async def test_check_allowed(app):
    r = await app.privacy.check(action="read_file", approved=False)
    assert r["allowed"] is True
    assert r["reason"] == "allowed"


@pytest.mark.asyncio
async def test_check_destructive_unapproved(app):
    r = await app.privacy.check(action="git_push", approved=False)
    assert r["allowed"] is False
    assert r["reason"] == "approval_required"


@pytest.mark.asyncio
async def test_check_destructive_approved(app):
    r = await app.privacy.check(action="delete_file", approved=True)
    assert r["allowed"] is True


@pytest.mark.asyncio
async def test_encrypt_snapshot(app):
    r = await app.privacy.encrypt_snapshot("local snapshot payload")
    assert r["accepted"] is True
    assert r["encrypted"] is True
    assert r["local_only"] is True
    assert "ciphertext" in r


@pytest.mark.asyncio
async def test_privacy_snapshot(app):
    await app.privacy.check(action="read_file")
    snap = app.privacy.snapshot()
    assert snap["audit_entries"] >= 1


@pytest.mark.asyncio
async def test_filter_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        privacy_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.privacy.filter_text("password=secret")
    assert r["accepted"] is False
    assert r["reason"] == "privacy_disabled"
    await odin.shutdown()


def test_filter_sensitive_unit():
    clean, triggered = filter_sensitive("normal text")
    assert triggered is False
    redacted, triggered2 = filter_sensitive("token=abc")
    assert triggered2 is True
    assert redacted == "[REDACTED]"


@pytest.mark.parametrize(
    "action,approved,expected",
    [
        ("git_push", False, False),
        ("send_email", False, False),
        ("shell_exec", True, True),
        ("list_files", False, True),
    ],
)
def test_check_permission_unit(action, approved, expected):
    allowed, _ = check_permission(action=action, approved=approved)
    assert allowed is expected


def test_encrypt_local_unit():
    enc = encrypt_local("payload", key_hint="test")
    assert enc["encrypted"] is True
    assert len(enc["ciphertext"]) == 32


def test_privacy_filter_triggered_channel():
    ev = TraceEvent(
        kind=TraceEventKind.PRIVACY_FILTER_TRIGGERED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "privacy:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(45))
@pytest.mark.asyncio
async def test_filter_clean_bulk(app, i):
    r = await app.privacy.filter_text(f"routine log line {i}")
    assert r["accepted"] is True
    assert r["filtered"] is False


@pytest.mark.parametrize("keyword", ["password", "secret", "api_key", "token", "API-KEY"])
@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_filter_sensitive_bulk(app, keyword, i):
    r = await app.privacy.filter_text(f"leaked {keyword}=value-{i}")
    assert r["accepted"] is True
    assert r["filtered"] is True


@pytest.mark.parametrize(
    "action",
    ["git_push", "delete_file", "send_email", "shell_exec", "read_file", "write_file"],
)
@pytest.mark.parametrize("approved", [True, False])
@pytest.mark.asyncio
async def test_check_matrix(app, action, approved):
    r = await app.privacy.check(action=action, approved=approved)
    destructive = action in {"git_push", "delete_file", "send_email", "shell_exec"}
    if destructive and not approved:
        assert r["allowed"] is False
    else:
        assert r["allowed"] is True


@pytest.mark.parametrize("payload", ["snap-a", "snap-b", "user-data", "session-state"])
@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_encrypt_snapshot_bulk(app, payload, i):
    r = await app.privacy.encrypt_snapshot(f"{payload}-{i}")
    assert r["accepted"] is True
    assert r["encrypted"] is True

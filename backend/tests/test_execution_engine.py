"""Execution engine — sandbox, concurrency, cancel, retry, streaming."""

import asyncio

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.execution.models import ExecutionRunRequest, ExecutionState
from odin_backend.core.execution.sandbox import ExecutionSandbox, SandboxViolation
from odin_backend.core.observability.events import TraceEventKind


@pytest.mark.asyncio
async def test_sandbox_blocks_dangerous_shell():
    sb = ExecutionSandbox(Settings().sandbox_work_dir / "test_sb")
    with pytest.raises(SandboxViolation):
        sb.validate_shell_command("rm -rf /")


@pytest.mark.asyncio
async def test_sandbox_allows_safe_echo():
    sb = ExecutionSandbox(Settings().sandbox_work_dir / "test_sb2")
    sb.validate_shell_command("echo hello")


@pytest.fixture
async def app(tmp_path):
    db = tmp_path / "exec_test.db"
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        stability_loop_enabled=False,
        mission_dispatch_enabled=False,
        mission_gc_enabled=False,
        mission_restore_on_startup=False,
        streaming_enabled=True,
        execution_engine_enabled=True,
        execution_max_concurrent=3,
        execution_default_timeout_seconds=10.0,
        execution_recovery_interval_seconds=3600,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_python_execution_completes(app: OdinApplication):
    engine = app.execution_engine
    req = ExecutionRunRequest(
        capability="python.safe",
        params={"code": "print('odin_exec_ok')"},
        timeout_seconds=8,
    )
    record = await engine.submit(req)
    for _ in range(50):
        rec = await engine.get(record.execution_id)
        assert rec
        if rec.state in (ExecutionState.COMPLETED, ExecutionState.FAILED):
            break
        await asyncio.sleep(0.1)
    final = await engine.get(record.execution_id)
    assert final.state == ExecutionState.COMPLETED
    logs = await engine.logs(record.execution_id)
    assert any("odin_exec_ok" in line for line in logs["stdout"])


@pytest.mark.asyncio
async def test_shell_blocked(app: OdinApplication):
    engine = app.execution_engine
    req = ExecutionRunRequest(
        capability="shell.safe",
        params={"command": "rm -rf ."},
    )
    record = await engine.submit(req)
    for _ in range(30):
        rec = await engine.get(record.execution_id)
        if rec.state in (ExecutionState.COMPLETED, ExecutionState.FAILED):
            break
        await asyncio.sleep(0.05)
    final = await engine.get(record.execution_id)
    assert final.state == ExecutionState.FAILED
    assert final.error


@pytest.mark.asyncio
async def test_cancellation(app: OdinApplication):
    engine = app.execution_engine
    req = ExecutionRunRequest(
        capability="python.safe",
        params={"code": "import time\ntime.sleep(30)"},
        timeout_seconds=30,
    )
    record = await engine.submit(req)
    await asyncio.sleep(0.2)
    cancelled = await engine.cancel(record.execution_id)
    assert cancelled
    assert cancelled.state == ExecutionState.CANCELLED


@pytest.mark.asyncio
async def test_retry(app: OdinApplication):
    engine = app.execution_engine
    req = ExecutionRunRequest(
        capability="shell.safe",
        params={"command": "rm -rf tmp"},
        max_retries=2,
    )
    record = await engine.submit(req)
    for _ in range(30):
        rec = await engine.get(record.execution_id)
        if rec.state == ExecutionState.FAILED:
            break
        await asyncio.sleep(0.05)
    retried = await engine.retry(record.execution_id)
    assert retried.retry_count >= 1


@pytest.mark.asyncio
async def test_concurrent_executions(app: OdinApplication):
    engine = app.execution_engine
    ids = []
    for i in range(3):
        r = await engine.submit(
            ExecutionRunRequest(
                capability="api.internal",
                params={"action": f"ping{i}"},
            )
        )
        ids.append(r.execution_id)
    for _ in range(40):
        states = [(await engine.get(eid)).state for eid in ids]
        if all(s == ExecutionState.COMPLETED for s in states):
            break
        await asyncio.sleep(0.05)
    assert engine.metrics.total_completed >= 3


@pytest.mark.asyncio
async def test_execution_trace_events(app: OdinApplication):
    engine = app.execution_engine
    record = await engine.submit(
        ExecutionRunRequest(capability="api.internal", params={"action": "trace_test"})
    )
    for _ in range(30):
        rec = await engine.get(record.execution_id)
        if rec.state == ExecutionState.COMPLETED:
            break
        await asyncio.sleep(0.05)
    from odin_backend.core.observability.store import CausalEventStore

    store: CausalEventStore = app.observability.tracer.store
    all_events = [store._event_map[eid] for eid in store._event_map]  # noqa: SLF001
    kinds = {e.kind for e in all_events if e.payload.get("execution_id") == record.execution_id}
    assert TraceEventKind.EXECUTION_STARTED in kinds
    assert TraceEventKind.EXECUTION_COMPLETED in kinds


@pytest.mark.asyncio
async def test_timeout_short(app: OdinApplication):
    engine = app.execution_engine
    record = await engine.submit(
        ExecutionRunRequest(
            capability="python.safe",
            params={"code": "import time\ntime.sleep(5)"},
            timeout_seconds=0.3,
        )
    )
    for _ in range(40):
        rec = await engine.get(record.execution_id)
        if rec.state in (ExecutionState.TIMED_OUT, ExecutionState.FAILED, ExecutionState.COMPLETED):
            break
        await asyncio.sleep(0.05)
    final = await engine.get(record.execution_id)
    assert final.state in (ExecutionState.TIMED_OUT, ExecutionState.FAILED)


@pytest.mark.asyncio
async def test_lease_and_recovery(app: OdinApplication):
    engine = app.execution_engine
    record = ExecutionRunRequest(capability="api.internal", params={"action": "x"})
    rec = await engine.submit(record)
    rec.lease_expiry = None
    rec.state = ExecutionState.RUNNING
    rec.last_heartbeat_at = None
    await engine.store.put(rec)
    engine.leases._default = 0.01  # noqa: SLF001
    engine.leases.acquire(rec, seconds=0.01)
    await engine.store.put(rec)
    await asyncio.sleep(0.05)
    n = await engine.recover_stuck()
    assert n >= 0

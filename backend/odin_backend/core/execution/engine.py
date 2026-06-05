"""ExecutionEngine — allocate, run, monitor, cancel, retry executions."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any

from odin_backend.core.execution.cancellation import CancellationRegistry
from odin_backend.core.execution.capabilities import CAPABILITIES, infer_execution_type
from odin_backend.core.execution.executor import build_default_registry
from odin_backend.core.execution.leases import LeaseManager
from odin_backend.core.execution.metrics import ExecutionMetrics
from odin_backend.core.execution.models import (
    ExecutionRecord,
    ExecutionRunRequest,
    ExecutionState,
    ExecutionType,
)
from odin_backend.core.execution.recovery import ExecutionRecoveryLoop
from odin_backend.core.execution.result_store import ExecutionResultStore
from odin_backend.core.execution.sandbox import ExecutionSandbox
from odin_backend.core.execution.stdout import StreamBufferRegistry
from odin_backend.core.observability.events import TraceEventKind
from odin_backend.core.observability.context import CausalTraceContext, bind_context
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_TERMINAL = {
    ExecutionState.COMPLETED,
    ExecutionState.FAILED,
    ExecutionState.CANCELLED,
    ExecutionState.TIMED_OUT,
}


class ExecutionEngine:
    def __init__(self, app: Any) -> None:
        settings = app.settings
        self._app = app
        self.store = ExecutionResultStore()
        self.streams = StreamBufferRegistry()
        self.sandbox = ExecutionSandbox(settings.sandbox_work_dir / "executions")
        self.leases = LeaseManager(default_seconds=settings.execution_lease_seconds)
        self.cancellations = CancellationRegistry()
        self.metrics = ExecutionMetrics()
        self.registry = build_default_registry(
            self.sandbox,
            self.streams,
            default_timeout=settings.execution_default_timeout_seconds,
        )
        self._sem = asyncio.Semaphore(settings.execution_max_concurrent)
        self._recovery = ExecutionRecoveryLoop(self, interval_seconds=settings.execution_recovery_interval_seconds)
        self._heartbeat_seconds = settings.execution_stuck_heartbeat_seconds
        self._retry_backoff = settings.execution_retry_backoff_seconds
        self._max_retries_default = settings.execution_retry_max

    async def start(self) -> None:
        await self._recovery.start()

    async def stop(self) -> None:
        await self._recovery.stop()

    async def submit(self, request: ExecutionRunRequest) -> ExecutionRecord:
        ex_type = request.execution_type
        if ex_type is None:
            ex_type = ExecutionType(infer_execution_type(request.capability))
        pool_name = "local"
        pool_mgr = getattr(self._app, "execution_pool_manager", None)
        if pool_mgr:
            pool = pool_mgr.route_pool(request.capability)
            pool_name = pool.name
        worker_id = getattr(self._app, "distributed_queue", None)
        wid = worker_id.worker_id if worker_id else None
        record = ExecutionRecord(
            mission_id=request.mission_id,
            task_id=request.task_id,
            executor_agent=request.executor_agent,
            capability_used=request.capability,
            execution_type=ex_type,
            params=request.params,
            max_retries=request.max_retries or self._max_retries_default,
            pool_name=pool_name,
            worker_id=wid,
        )
        out = self.streams.get_or_create(record.execution_id, "stdout")
        err = self.streams.get_or_create(record.execution_id, "stderr")
        record.stdout_ref = out.ref
        record.stderr_ref = err.ref
        await self.store.put(record)
        await self._emit_trace(TraceEventKind.EXECUTION_ALLOCATED, record, "execution allocated")
        if pool_mgr:
            pool = pool_mgr.get(pool_name)
            asyncio.create_task(pool.run(lambda: self._execute_lifecycle(record, request.timeout_seconds)))
        else:
            asyncio.create_task(self._execute_lifecycle(record, request.timeout_seconds))
        return record

    async def cancel(self, execution_id: str, *, reason: str = "user_cancel") -> ExecutionRecord | None:
        record = await self.store.get(execution_id)
        if not record or record.state in _TERMINAL:
            return record
        self.cancellations.cancel(execution_id)
        updated = await self._transition(
            execution_id,
            ExecutionState.CANCELLED,
            error=reason,
        )
        if updated:
            await self._emit_trace(TraceEventKind.EXECUTION_CANCELLED, updated, reason)
            self.metrics.total_cancelled += 1
        return updated

    async def retry(self, execution_id: str) -> ExecutionRecord | None:
        record = await self.store.get(execution_id)
        if not record:
            return None
        if record.retry_count >= record.max_retries:
            return record
        req = ExecutionRunRequest(
            capability=record.capability_used,
            mission_id=record.mission_id,
            task_id=record.task_id,
            executor_agent=record.executor_agent,
            execution_type=record.execution_type,
            params=record.params,
            max_retries=record.max_retries,
        )
        record.retry_count += 1
        record.state = ExecutionState.RETRYING
        record.error = None
        record.exit_code = None
        record.ended_at = None
        await self.store.put(record)
        self.metrics.total_retries += 1
        await self._emit_trace(
            TraceEventKind.EXECUTION_RETRY,
            record,
            f"retry {record.retry_count}/{record.max_retries}",
        )
        asyncio.create_task(self._execute_lifecycle(record, None))
        return record

    async def get(self, execution_id: str) -> ExecutionRecord | None:
        return await self.store.get(execution_id)

    async def wait_for(
        self,
        execution_id: str,
        *,
        timeout: float = 120.0,
        poll_interval: float = 0.1,
    ) -> ExecutionRecord | None:
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            rec = await self.store.get(execution_id)
            if rec and rec.state in _TERMINAL:
                return rec
            await asyncio.sleep(poll_interval)
        return await self.store.get(execution_id)

    async def logs(self, execution_id: str, *, tail: int = 500) -> dict:
        rec = await self.store.get(execution_id)
        if not rec:
            return {"stdout": [], "stderr": []}
        out = self.streams.get(rec.stdout_ref)
        err = self.streams.get(rec.stderr_ref)
        return {
            "stdout": out.snapshot(tail=tail) if out else [],
            "stderr": err.snapshot(tail=tail) if err else [],
        }

    async def list_executions(self, *, limit: int = 100) -> list[ExecutionRecord]:
        return await self.store.list_all(limit=limit)

    async def recover_stuck(self) -> int:
        recovered = 0
        for record in await self.store.list_active():
            expired = self.leases.is_expired(record)
            stuck = ExecutionRecoveryLoop.is_stuck(
                record,
                heartbeat_seconds=self._heartbeat_seconds,
                lease_expired=expired,
            )
            if not stuck:
                continue
            self.cancellations.cancel(record.execution_id)
            state = ExecutionState.TIMED_OUT if expired else ExecutionState.FAILED
            updated = await self._transition(
                record.execution_id,
                state,
                error="stuck_or_lease_expired",
            )
            if updated:
                kind = (
                    TraceEventKind.EXECUTION_TIMEOUT
                    if state == ExecutionState.TIMED_OUT
                    else TraceEventKind.EXECUTION_FAILED
                )
                await self._emit_trace(kind, updated, "orphan recovery")
                recovered += 1
        return recovered

    async def _execute_lifecycle(
        self,
        record: ExecutionRecord,
        timeout_override: float | None,
    ) -> None:
        async with self._sem:
            self.metrics.active_count += 1
            self.metrics.total_started += 1
            try:
                await self._run(record, timeout_override)
            finally:
                self.metrics.active_count = max(0, self.metrics.active_count - 1)
                self.cancellations.drop(record.execution_id)
                self.leases.release(record.execution_id)

    async def _run(self, record: ExecutionRecord, timeout_override: float | None) -> None:
        executor = self.registry.get(record.capability_used)
        if not executor:
            await self._fail(record.execution_id, f"no executor for {record.capability_used}")
            return

        spec = CAPABILITIES.get(record.capability_used) or self.registry.spec(record.capability_used)
        timeout = timeout_override or spec.default_timeout_seconds or executor.default_timeout

        await self._transition(record.execution_id, ExecutionState.ALLOCATED)
        record = await self.store.get(record.execution_id) or record
        self.leases.acquire(record, seconds=timeout + 60)
        await self.store.put(record)

        tok = self.cancellations.register(record.execution_id)
        cancel_event = tok._event

        await self._transition(record.execution_id, ExecutionState.RUNNING)
        record = await self.store.get(record.execution_id) or record
        record.started_at = datetime.now(timezone.utc)
        record.touch_heartbeat()
        await self.store.put(record)
        await self._emit_trace(TraceEventKind.EXECUTION_STARTED, record, "execution running")

        ctx_kw2: dict[str, Any] = {}
        if record.mission_id:
            ctx_kw2["mission_id"] = record.mission_id
        if record.task_id:
            ctx_kw2["task_id"] = record.task_id
        if record.trace_id:
            ctx_kw2["trace_id"] = record.trace_id
        bind_context(CausalTraceContext(**ctx_kw2))

        async def on_progress(msg: str, payload: dict) -> None:
            rec = await self.store.get(record.execution_id)
            if rec:
                rec.touch_heartbeat()
                await self.store.put(rec)
                await self._emit_trace(
                    TraceEventKind.EXECUTION_PROGRESS,
                    rec,
                    msg,
                    payload=payload,
                )

        async def on_line(kind: str, line: str, execution_id: str) -> None:
            buf = self.streams.get_or_create(execution_id, kind)
            buf.append(line)
            rec = await self.store.get(execution_id)
            if not rec:
                return
            trace_kind = (
                TraceEventKind.EXECUTION_STDOUT
                if kind == "stdout"
                else TraceEventKind.EXECUTION_STDERR
            )
            await self._emit_trace(trace_kind, rec, line[:500], payload={"line": line[:2000]})
            stream_kind = (
                TraceEventKind.EXECUTION_STDOUT
                if kind == "stdout"
                else TraceEventKind.EXECUTION_STDERR
            )
            await self._emit_stream(stream_kind.value, rec, line[:500], payload={"stream": kind, "line": line})

        task = asyncio.create_task(
            executor.run(
                record,
                record.params,
                cancel_event=cancel_event,
                on_progress=on_progress,
                on_line=on_line,
            )
        )
        self.cancellations.bind_task(record.execution_id, task)

        try:
            result = await asyncio.wait_for(task, timeout=timeout)
        except asyncio.TimeoutError:
            self.cancellations.cancel(record.execution_id)
            await self._timeout(record.execution_id)
            return
        except asyncio.CancelledError:
            await self._cancelled(record.execution_id)
            return

        if cancel_event.is_set():
            await self._cancelled(record.execution_id)
            return

        if result.success:
            await self._complete(record.execution_id, result.output, result.exit_code)
        else:
            err = result.error or "execution_failed"
            if result.error == "timed_out":
                await self._timeout(record.execution_id)
            else:
                await self._fail(record.execution_id, err, exit_code=result.exit_code)

    async def _complete(
        self,
        execution_id: str,
        output: dict,
        exit_code: int | None,
    ) -> None:
        updated = await self._transition(
            execution_id,
            ExecutionState.COMPLETED,
            result=output,
            exit_code=exit_code or 0,
        )
        if updated:
            self.metrics.record_completion(ts=time.time())
            await self._emit_trace(TraceEventKind.EXECUTION_COMPLETED, updated, "completed")
            await self._maybe_rollback(updated, success=True)

    async def _fail(
        self,
        execution_id: str,
        error: str,
        *,
        exit_code: int | None = None,
    ) -> None:
        updated = await self._transition(
            execution_id,
            ExecutionState.FAILED,
            error=error,
            exit_code=exit_code,
        )
        if updated:
            self.metrics.total_failed += 1
            await self._emit_trace(TraceEventKind.EXECUTION_FAILED, updated, error)
            await self._maybe_rollback(updated, success=False)

    async def _timeout(self, execution_id: str) -> None:
        updated = await self._transition(
            execution_id,
            ExecutionState.TIMED_OUT,
            error="timed_out",
        )
        if updated:
            self.metrics.total_timed_out += 1
            await self._emit_trace(TraceEventKind.EXECUTION_TIMEOUT, updated, "timed out")

    async def _cancelled(self, execution_id: str) -> None:
        updated = await self._transition(
            execution_id,
            ExecutionState.CANCELLED,
            error="cancelled",
        )
        if updated:
            self.metrics.total_cancelled += 1
            await self._emit_trace(TraceEventKind.EXECUTION_CANCELLED, updated, "cancelled")

    async def _maybe_rollback(self, record: ExecutionRecord, *, success: bool) -> None:
        if success or not record.rollback_reference:
            return
        await self._transition(record.execution_id, ExecutionState.ROLLING_BACK)
        await self._emit_trace(
            TraceEventKind.EXECUTION_ROLLBACK,
            record,
            f"rollback {record.rollback_reference}",
        )
        self.sandbox.cleanup_workspace(record.execution_id)

    async def _transition(
        self,
        execution_id: str,
        state: ExecutionState,
        *,
        fencing_token: int | None = None,
        **fields: Any,
    ) -> ExecutionRecord | None:
        rec = await self.store.get(execution_id)
        if not rec:
            return None
        if not self.leases.validate_fence(rec, fencing_token):
            logger.warning(
                "execution_fence_rejected",
                execution_id=execution_id,
                expected=rec.fencing_token,
            )
            return None
        rec.state = state
        for k, v in fields.items():
            setattr(rec, k, v)
        if state in _TERMINAL:
            rec.ended_at = datetime.now(timezone.utc)
            self.leases.release(execution_id)
        await self.store.put(rec)
        return rec

    async def _emit_trace(
        self,
        kind: TraceEventKind,
        record: ExecutionRecord,
        message: str,
        *,
        payload: dict | None = None,
    ) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        pl = {
            "execution_id": record.execution_id,
            "state": record.state.value,
            "capability": record.capability_used,
            **(payload or {}),
        }
        ctx_kw: dict[str, Any] = {}
        if record.mission_id:
            ctx_kw["mission_id"] = record.mission_id
        if record.task_id:
            ctx_kw["task_id"] = record.task_id
        if record.trace_id:
            ctx_kw["trace_id"] = record.trace_id
        ctx = CausalTraceContext(**ctx_kw)
        obs.tracer.record(
            kind,
            message=message,
            payload=pl,
            component="execution_engine",
            ctx=ctx,
        )

    async def _emit_stream(
        self,
        event_type: str,
        record: ExecutionRecord,
        message: str,
        *,
        payload: dict | None = None,
    ) -> None:
        from odin_backend.core.streaming.bridge import get_stream_bridge
        from odin_backend.core.streaming.serializers import StreamEnvelope, StreamEventKind

        bridge = get_stream_bridge()
        if not bridge:
            return
        try:
            kind = StreamEventKind(event_type)
        except ValueError:
            kind = StreamEventKind.SIGNAL_PROPAGATED
        envelope = StreamEnvelope(
            event_type=kind,
            channel=f"execution:{record.execution_id}",
            execution_id=record.execution_id,
            mission_id=record.mission_id,
            task_id=record.task_id,
            trace_id=record.trace_id,
            message=message,
            payload={
                "execution_id": record.execution_id,
                "state": record.state.value,
                **(payload or {}),
            },
            component="execution_engine",
        )
        bridge.bus.publish_nowait(envelope)

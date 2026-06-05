"""Concrete executors — Python, shell, file, workflow."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any, Callable, Awaitable

from odin_backend.core.execution.models import ExecutionRecord, ExecutionType
from odin_backend.core.execution.registry import BaseExecutor, ExecutorResult
from odin_backend.core.execution.sandbox import ExecutionSandbox, SandboxViolation
from odin_backend.core.execution.stdout import StreamBufferRegistry
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

ProgressCb = Callable[[str, dict], Awaitable[None]]
LineCb = Callable[[str, str, str], Awaitable[None]]  # kind, line, execution_id


async def _run_subprocess(
    record: ExecutionRecord,
    cmd: list[str],
    *,
    cwd: Path,
    timeout: float,
    cancel_event: asyncio.Event,
    on_line: LineCb,
) -> ExecutorResult:
    stdout_buf = record.stdout_ref
    stderr_buf = record.stderr_ref
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    async def pump(stream: asyncio.StreamReader, kind: str) -> None:
        while True:
            line = await stream.readline()
            if not line:
                break
            text = line.decode(errors="replace").rstrip("\n\r")
            await on_line(kind, text, record.execution_id)

    stdout_task = asyncio.create_task(pump(proc.stdout, "stdout"))  # type: ignore[arg-type]
    stderr_task = asyncio.create_task(pump(proc.stderr, "stderr"))  # type: ignore[arg-type]
    try:
        if cancel_event.is_set():
            proc.kill()
            await proc.wait()
            return ExecutorResult(success=False, exit_code=-1, error="cancelled")
        await asyncio.wait_for(proc.wait(), timeout=timeout)
        await asyncio.wait_for(
            asyncio.gather(stdout_task, stderr_task, return_exceptions=True),
            timeout=2.0,
        )
        code = proc.returncode or 0
        return ExecutorResult(
            success=code == 0,
            exit_code=code,
            output={"stdout_ref": stdout_buf, "stderr_ref": stderr_buf},
            error=None if code == 0 else f"exit {code}",
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        stdout_task.cancel()
        stderr_task.cancel()
        return ExecutorResult(success=False, exit_code=-9, error="timed_out")
    except asyncio.CancelledError:
        proc.kill()
        await proc.wait()
        return ExecutorResult(success=False, exit_code=-1, error="cancelled")


class PythonSafeExecutor(BaseExecutor):
    capability = "python.safe"
    execution_type = ExecutionType.PYTHON

    async def run(
        self,
        record: ExecutionRecord,
        params: dict[str, Any],
        *,
        cancel_event: asyncio.Event,
        on_progress: ProgressCb,
        on_line: LineCb,
    ) -> ExecutorResult:
        source = params.get("code") or params.get("source") or 'print("ok")'
        self.sandbox.validate_python_source(str(source))
        workspace = self.sandbox.workspace_for(record.execution_id)
        script = workspace / "_script.py"
        script.write_text(str(source), encoding="utf-8")
        await on_progress("writing script", {"path": str(script)})
        timeout = float(params.get("timeout_seconds", self.default_timeout))
        return await _run_subprocess(
            record,
            [sys.executable, str(script)],
            cwd=workspace,
            timeout=timeout,
            cancel_event=cancel_event,
            on_line=on_line,
        )


class ShellSafeExecutor(BaseExecutor):
    capability = "shell.safe"
    execution_type = ExecutionType.SHELL

    async def run(
        self,
        record: ExecutionRecord,
        params: dict[str, Any],
        *,
        cancel_event: asyncio.Event,
        on_progress: ProgressCb,
        on_line: LineCb,
    ) -> ExecutorResult:
        command = str(params.get("command", "echo hello"))
        try:
            self.sandbox.validate_shell_command(command)
        except SandboxViolation as exc:
            return ExecutorResult(success=False, exit_code=1, error=str(exc))
        workspace = self.sandbox.workspace_for(record.execution_id)
        await on_progress("shell", {"command": command[:200]})
        timeout = float(params.get("timeout_seconds", self.default_timeout))
        if sys.platform == "win32":
            cmd = ["cmd", "/c", command]
        else:
            cmd = ["sh", "-c", command]
        return await _run_subprocess(
            record,
            cmd,
            cwd=workspace,
            timeout=timeout,
            cancel_event=cancel_event,
            on_line=on_line,
        )


class FileProcessingExecutor(BaseExecutor):
    capability = "filesystem.read"
    execution_type = ExecutionType.FILE

    async def run(
        self,
        record: ExecutionRecord,
        params: dict[str, Any],
        *,
        cancel_event: asyncio.Event,
        on_progress: ProgressCb,
        on_line: LineCb,
    ) -> ExecutorResult:
        workspace = self.sandbox.workspace_for(record.execution_id)
        op = params.get("op", "read")
        rel = str(params.get("path", "input.txt"))
        try:
            path = self.sandbox.resolve_path(workspace, rel)
        except SandboxViolation as exc:
            return ExecutorResult(success=False, error=str(exc))
        if cancel_event.is_set():
            return ExecutorResult(success=False, error="cancelled")
        if op == "write":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(params.get("content", "")), encoding="utf-8")
            await on_line("stdout", f"wrote {path.name}", record.execution_id)
            return ExecutorResult(success=True, output={"path": str(path)})
        if not path.exists():
            return ExecutorResult(success=False, error="file not found")
        content = path.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines()[:50]:
            await on_line("stdout", line, record.execution_id)
        return ExecutorResult(success=True, output={"content": content[:8000], "path": str(path)})


class FileWriteExecutor(FileProcessingExecutor):
    capability = "filesystem.write"

    async def run(
        self,
        record: ExecutionRecord,
        params: dict[str, Any],
        *,
        cancel_event: asyncio.Event,
        on_progress: ProgressCb,
        on_line: LineCb,
    ) -> ExecutorResult:
        params = {**params, "op": "write"}
        return await super().run(
            record, params, cancel_event=cancel_event, on_progress=on_progress, on_line=on_line
        )


class InternalWorkflowExecutor(BaseExecutor):
    capability = "workflow.execute"
    execution_type = ExecutionType.WORKFLOW

    async def run(
        self,
        record: ExecutionRecord,
        params: dict[str, Any],
        *,
        cancel_event: asyncio.Event,
        on_progress: ProgressCb,
        on_line: LineCb,
    ) -> ExecutorResult:
        steps = params.get("steps") or [{"action": "noop"}]
        await on_progress("workflow_start", {"steps": len(steps)})
        for i, step in enumerate(steps):
            if cancel_event.is_set():
                return ExecutorResult(success=False, error="cancelled")
            await on_line("stdout", f"step {i}: {step}", record.execution_id)
            await asyncio.sleep(0.01)
        await on_progress("workflow_done", {})
        return ExecutorResult(success=True, output={"steps_completed": len(steps)})


class InternalApiExecutor(BaseExecutor):
    capability = "api.internal"
    execution_type = ExecutionType.PYTHON

    async def run(
        self,
        record: ExecutionRecord,
        params: dict[str, Any],
        *,
        cancel_event: asyncio.Event,
        on_progress: ProgressCb,
        on_line: LineCb,
    ) -> ExecutorResult:
        action = params.get("action", "ping")
        await on_line("stdout", f"internal:{action}", record.execution_id)
        return ExecutorResult(success=True, output={"action": action, "pong": True})


def build_default_registry(
    sandbox: ExecutionSandbox,
    streams: StreamBufferRegistry,
    *,
    default_timeout: float,
) -> "ExecutorRegistry":
    from odin_backend.core.execution.registry import ExecutorRegistry

    reg = ExecutorRegistry()
    kw = {"sandbox": sandbox, "streams": streams, "default_timeout": default_timeout}
    reg.register("python.safe", PythonSafeExecutor(**kw))
    reg.register("shell.safe", ShellSafeExecutor(**kw))
    reg.register("filesystem.read", FileProcessingExecutor(**kw))
    reg.register("filesystem.write", FileWriteExecutor(**kw))
    reg.register("workflow.execute", InternalWorkflowExecutor(**kw))
    reg.register("api.internal", InternalApiExecutor(**kw))
    return reg

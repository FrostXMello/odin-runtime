"""Sandbox execution adapter — local workspace isolation."""

from __future__ import annotations

from typing import Any

from odin_backend.core.execution.adapters.executor_adapter import ExecutorAdapter, LocalSubprocessAdapter


class SandboxAdapter(LocalSubprocessAdapter):
    """Wraps local subprocess execution with sandbox semantics."""

    def __init__(self, sandbox_work_dir: Any) -> None:
        self._work_dir = sandbox_work_dir

    async def start(self, *, execution_id: str, spec: dict[str, Any]) -> dict[str, Any]:
        workspace = self._work_dir / execution_id
        workspace.mkdir(parents=True, exist_ok=True)
        return {
            "execution_id": execution_id,
            "adapter": "sandbox",
            "workspace": str(workspace),
            "started": True,
        }

    async def health(self) -> dict[str, Any]:
        return {"status": "healthy", "adapter": "sandbox", "work_dir": str(self._work_dir)}


def get_sandbox_adapter(sandbox_work_dir: Any) -> ExecutorAdapter:
    return SandboxAdapter(sandbox_work_dir)

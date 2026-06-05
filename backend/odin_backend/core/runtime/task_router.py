"""Route task contracts to capabilities and execution requests."""

from __future__ import annotations

from typing import Any

from odin_backend.core.execution.capabilities import CAPABILITIES
from odin_backend.core.execution.models import ExecutionRunRequest, ExecutionType
from odin_backend.core.execution.sandbox import SandboxViolation
from odin_backend.core.runtime.task_contracts import TaskContractType, TaskExecutionContract
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_FALLBACK_CAPABILITY = "api.internal"


class TaskRouter:
    """Validates contracts and builds ExecutionRunRequest objects."""

    def validate(self, contract: TaskExecutionContract) -> tuple[bool, str]:
        if contract.type == TaskContractType.NOOP:
            return True, "noop"
        if contract.type == TaskContractType.TOOL:
            return True, "tool_pipeline"
        cap = self.resolve_capability(contract)
        if cap not in CAPABILITIES and contract.type not in (
            TaskContractType.WORKFLOW,
            TaskContractType.TOOL,
        ):
            return False, f"unknown capability: {cap}"
        if contract.type == TaskContractType.SHELL:
            cmd = contract.params.get("command", "")
            try:
                from odin_backend.core.execution.sandbox import ExecutionSandbox
                from pathlib import Path

                sb = ExecutionSandbox(Path("./data/sandbox/executions"))
                sb.validate_shell_command(str(cmd))
            except SandboxViolation as exc:
                return False, str(exc)
        return True, "ok"

    def resolve_capability(self, contract: TaskExecutionContract) -> str:
        if contract.type == TaskContractType.SHELL:
            return contract.capability or "shell.safe"
        if contract.type == TaskContractType.WORKFLOW:
            return "workflow.execute"
        if contract.type == TaskContractType.INTERNAL_API:
            return "api.internal"
        if contract.type == TaskContractType.MEMORY:
            return contract.capability or "filesystem.write"
        if contract.type == TaskContractType.EXECUTION:
            return contract.capability or "python.safe"
        if contract.type in (TaskContractType.GRAPH, TaskContractType.DIAGNOSTICS):
            return "api.internal"
        return contract.capability or _FALLBACK_CAPABILITY

    def to_run_request(
        self,
        contract: TaskExecutionContract,
        *,
        mission_id: str,
        task_id: str,
        executor_agent: str,
        app: Any,
    ) -> ExecutionRunRequest | None:
        if contract.type in (TaskContractType.NOOP, TaskContractType.TOOL):
            return None
        cap = self.resolve_capability(contract)
        timeout = contract.timeout_seconds
        if timeout is None and hasattr(app, "settings"):
            spec = CAPABILITIES.get(cap)
            timeout = spec.default_timeout_seconds if spec else app.settings.execution_default_timeout_seconds

        ex_type = None
        if contract.type == TaskContractType.SHELL:
            ex_type = ExecutionType.SHELL
        elif contract.type == TaskContractType.WORKFLOW:
            ex_type = ExecutionType.WORKFLOW
        elif contract.type == TaskContractType.MEMORY:
            ex_type = ExecutionType.FILE

        params = dict(contract.params)
        if contract.workflow and "steps" not in params:
            params.setdefault("steps", [{"action": contract.workflow}])

        return ExecutionRunRequest(
            capability=cap,
            mission_id=mission_id,
            task_id=task_id,
            executor_agent=executor_agent or "brokk",
            execution_type=ex_type,
            params=params,
            timeout_seconds=timeout,
        )

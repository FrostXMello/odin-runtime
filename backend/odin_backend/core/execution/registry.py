"""Capability-based executor registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from odin_backend.core.execution.capabilities import CAPABILITIES, CapabilitySpec
from odin_backend.core.execution.models import ExecutionRecord, ExecutionType
from odin_backend.core.execution.sandbox import ExecutionSandbox
from odin_backend.core.execution.stdout import StreamBufferRegistry


@dataclass
class ExecutorResult:
    success: bool
    exit_code: int = 0
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class BaseExecutor(ABC):
    capability: str
    execution_type: ExecutionType

    def __init__(
        self,
        *,
        sandbox: ExecutionSandbox,
        streams: StreamBufferRegistry,
        default_timeout: float = 120.0,
    ) -> None:
        self.sandbox = sandbox
        self.streams = streams
        self.default_timeout = default_timeout

    @abstractmethod
    async def run(
        self,
        record: ExecutionRecord,
        params: dict[str, Any],
        *,
        cancel_event: Any,
        on_progress: Any,
        on_line: Any,
    ) -> ExecutorResult:
        ...


class ExecutorRegistry:
    def __init__(self) -> None:
        self._executors: dict[str, BaseExecutor] = {}

    def register(self, capability: str, executor: BaseExecutor) -> None:
        self._executors[capability] = executor

    def get(self, capability: str) -> BaseExecutor | None:
        return self._executors.get(capability)

    def spec(self, capability: str) -> CapabilitySpec:
        return CAPABILITIES.get(capability, CapabilitySpec(capability))

    def capabilities(self) -> list[str]:
        return list(self._executors.keys())

"""Local in-process execution pool."""

from odin_backend.core.execution.pools.pool_manager import ExecutionPool

LocalExecutionPool = ExecutionPool

__all__ = ["LocalExecutionPool"]

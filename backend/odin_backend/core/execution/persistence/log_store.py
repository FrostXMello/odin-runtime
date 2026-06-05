"""Execution log persistence helpers."""

from odin_backend.core.execution.persistence.execution_store import SqliteExecutionStore

LogStore = SqliteExecutionStore

__all__ = ["LogStore"]

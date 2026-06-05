"""Execution profiling metrics."""

from __future__ import annotations

from typing import Any


class ExecutionProfiler:
    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, Any]] = {}

    def update(self, execution_id: str, **fields: Any) -> None:
        prof = self._profiles.setdefault(execution_id, {})
        prof.update(fields)

    def get(self, execution_id: str) -> dict[str, Any]:
        return self._profiles.get(execution_id, {})

    def snapshot(self, *, limit: int = 50) -> list[dict[str, Any]]:
        items = list(self._profiles.items())[-limit:]
        return [{"execution_id": k, **v} for k, v in items]

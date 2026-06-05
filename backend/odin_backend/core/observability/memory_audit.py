"""Memory mutation observability and audit trail."""

from __future__ import annotations

import hashlib
from collections import deque
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.core.observability.context import current_context


def _hash_value(value: Any) -> str:
    text = str(value) if not isinstance(value, (dict, list)) else str(sorted(str(value).encode()))
    return hashlib.sha256(text.encode()).hexdigest()[:16]


class MemoryMutationRecord(BaseModel):
    mutation_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str | None = None
    span_id: str | None = None
    causal_chain_id: str | None = None
    mission_id: str | None = None
    task_id: str | None = None
    actor: str = "system"
    reason: str = ""
    category: str = "general"
    memory_id: str | None = None
    previous_hash: str | None = None
    new_hash: str | None = None
    rollback_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryMutationAudit:
    def __init__(self, *, max_records: int = 10_000) -> None:
        self._records: deque[MemoryMutationRecord] = deque(maxlen=max_records)
        self._by_mission: dict[str, list[str]] = {}

    def record(
        self,
        *,
        actor: str,
        reason: str,
        category: str = "general",
        memory_id: str | None = None,
        previous_value: Any = None,
        new_value: Any = None,
        mission_id: str | None = None,
        task_id: str | None = None,
        rollback_ref: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryMutationRecord:
        ctx = current_context()
        rec = MemoryMutationRecord(
            trace_id=ctx.trace_id if ctx else None,
            span_id=ctx.span_id if ctx else None,
            causal_chain_id=ctx.causal_chain_id if ctx else None,
            mission_id=mission_id or (ctx.mission_id if ctx else None),
            task_id=task_id or (ctx.task_id if ctx else None),
            actor=actor,
            reason=reason,
            category=category,
            memory_id=memory_id,
            previous_hash=_hash_value(previous_value) if previous_value is not None else None,
            new_hash=_hash_value(new_value) if new_value is not None else None,
            rollback_ref=rollback_ref,
            metadata=metadata or {},
        )
        self._records.append(rec)
        mid = rec.mission_id
        if mid:
            self._by_mission.setdefault(mid, []).append(rec.mutation_id)
        return rec

    def for_mission(self, mission_id: str, limit: int = 100) -> list[MemoryMutationRecord]:
        ids = self._by_mission.get(mission_id, [])
        out: list[MemoryMutationRecord] = []
        for rec in reversed(self._records):
            if rec.mutation_id in ids or rec.mission_id == mission_id:
                out.append(rec)
            if len(out) >= limit:
                break
        return list(reversed(out))

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        return [r.model_dump(mode="json") for r in list(self._records)[-limit:]]

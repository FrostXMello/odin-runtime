"""Execution lease acquisition, expiry, and fencing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from odin_backend.core.execution.models import ExecutionRecord


class LeaseManager:
    def __init__(self, default_seconds: float = 300.0) -> None:
        self._default = default_seconds
        self._fence_counter = 0
        self._active_fences: dict[str, int] = {}

    def next_fence(self) -> int:
        self._fence_counter += 1
        return self._fence_counter

    def acquire(
        self,
        record: ExecutionRecord,
        *,
        seconds: float | None = None,
    ) -> datetime:
        ttl = seconds if seconds is not None else self._default
        expiry = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        record.lease_expiry = expiry
        fence = self.next_fence()
        record.fencing_token = fence
        self._active_fences[record.execution_id] = fence
        return expiry

    def is_expired(self, record: ExecutionRecord) -> bool:
        if not record.lease_expiry:
            return False
        return datetime.now(timezone.utc) > record.lease_expiry

    def renew(self, record: ExecutionRecord, *, seconds: float | None = None) -> datetime:
        return self.acquire(record, seconds=seconds)

    def validate_fence(self, record: ExecutionRecord, token: int | None = None) -> bool:
        expected = token if token is not None else record.fencing_token
        active = self._active_fences.get(record.execution_id)
        if expected is None and active is None:
            return True
        if expected is None or active is None:
            return False
        return expected == active

    def release(self, execution_id: str) -> None:
        self._active_fences.pop(execution_id, None)

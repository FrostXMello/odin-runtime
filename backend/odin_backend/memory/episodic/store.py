"""In-process episodic log with optional persistence hooks."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EpisodicEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    event: str
    payload: dict[str, Any]
    session_id: str | None = None
    workflow_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EpisodicStore:
    def __init__(self, max_entries: int = 5000) -> None:
        self._entries: list[EpisodicEntry] = []
        self._max = max_entries

    async def record(
        self,
        event: str,
        payload: dict[str, Any],
        *,
        session_id: str | None = None,
        workflow_id: str | None = None,
    ) -> EpisodicEntry:
        entry = EpisodicEntry(
            event=event,
            payload=payload,
            session_id=session_id,
            workflow_id=workflow_id,
        )
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]
        return entry

    async def query(
        self,
        *,
        workflow_id: str | None = None,
        session_id: str | None = None,
        limit: int = 50,
    ) -> list[EpisodicEntry]:
        results = self._entries
        if workflow_id:
            results = [e for e in results if e.workflow_id == workflow_id]
        if session_id:
            results = [e for e in results if e.session_id == session_id]
        return list(reversed(results[-limit:]))

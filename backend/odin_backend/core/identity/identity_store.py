"""SQLite-backed identity persistence."""

from __future__ import annotations

import json

import aiosqlite

from odin_backend.config import Settings
from odin_backend.core.identity.identity_state import IdentityState

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_identity_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    state_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class IdentityStore:
    def __init__(self, settings: Settings) -> None:
        self._path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None
        self._state = IdentityState()

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._path)
        await self._db.executescript(_SCHEMA)
        await self._db.commit()
        await self._load()

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    @property
    def state(self) -> IdentityState:
        return self._state

    async def _load(self) -> None:
        if not self._db:
            return
        async with self._db.execute("SELECT state_json FROM odin_identity_state WHERE id=1") as cur:
            row = await cur.fetchone()
        if row:
            self._state = IdentityState.model_validate(json.loads(row[0]))

    async def save(self) -> IdentityState:
        if not self._db:
            return self._state
        payload = self._state.model_dump(mode="json")
        await self._db.execute(
            """INSERT INTO odin_identity_state (id, state_json, updated_at) VALUES (1, ?, ?)
               ON CONFLICT(id) DO UPDATE SET state_json=excluded.state_json, updated_at=excluded.updated_at""",
            (json.dumps(payload), self._state.updated_at.isoformat()),
        )
        await self._db.commit()
        return self._state

    async def update(self, patch: dict) -> IdentityState:
        self._state = self._state.apply_bounded_update(patch)
        await self.save()
        return self._state

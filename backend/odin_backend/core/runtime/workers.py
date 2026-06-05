"""Distributed worker identity, heartbeat, and capability advertisement."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import aiosqlite

from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_runtime_workers (
    worker_id TEXT PRIMARY KEY,
    capabilities TEXT NOT NULL DEFAULT '[]',
    concurrency INTEGER NOT NULL DEFAULT 1,
    heartbeat_at TEXT NOT NULL,
    active_leases INTEGER NOT NULL DEFAULT 0,
    metadata TEXT NOT NULL DEFAULT '{}',
    draining INTEGER NOT NULL DEFAULT 0
);
"""


class WorkerRegistry:
    def __init__(self, settings: Settings, worker_id: str) -> None:
        self.worker_id = worker_id
        self._settings = settings
        caps_raw = settings.worker_capabilities or ""
        self._capabilities = [c.strip() for c in caps_raw.split(",") if c.strip()]
        if not self._capabilities:
            self._capabilities = ["mission_dispatch", "execution", "python.safe", "shell.safe"]
        self._concurrency = settings.mission_max_concurrent_missions
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None
        self._task: Any = None
        self._draining = False

    @property
    def capabilities(self) -> list[str]:
        return list(self._capabilities)

    async def connect(self) -> None:
        if not self._settings.queue_persist_enabled:
            return
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.executescript(_SCHEMA)
        try:
            await self._db.execute(
                "ALTER TABLE odin_runtime_workers ADD COLUMN draining INTEGER NOT NULL DEFAULT 0"
            )
        except Exception:
            pass
        await self._db.commit()
        await self.register()

    async def disconnect(self) -> None:
        if self._task:
            self._task.cancel()
        if self._db:
            await self._db.close()
            self._db = None

    async def register(self, *, capabilities: list[str] | None = None) -> None:
        if capabilities:
            self._capabilities = capabilities
        await self.heartbeat()

    async def heartbeat(self, *, active_leases: int = 0) -> None:
        if not self._db:
            return
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            """INSERT INTO odin_runtime_workers
               (worker_id, capabilities, concurrency, heartbeat_at, active_leases, metadata, draining)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(worker_id) DO UPDATE SET
                 capabilities=excluded.capabilities,
                 heartbeat_at=excluded.heartbeat_at,
                 active_leases=excluded.active_leases,
                 draining=excluded.draining""",
            (
                self.worker_id,
                json.dumps(self._capabilities),
                self._concurrency,
                now,
                active_leases,
                json.dumps({"node": "local", "draining": self._draining}),
                1 if self._draining else 0,
            ),
        )
        await self._db.commit()

    async def set_draining(self, draining: bool = True) -> None:
        self._draining = draining
        await self.heartbeat()

    async def list_workers(self, *, stale_seconds: float = 120.0) -> list[dict[str, Any]]:
        if not self._db:
            return [
                {
                    "worker_id": self.worker_id,
                    "local": True,
                    "capabilities": self._capabilities,
                    "heartbeat_at": datetime.now(timezone.utc).isoformat(),
                    "draining": self._draining,
                }
            ]
        out: list[dict[str, Any]] = []
        cutoff = datetime.now(timezone.utc).timestamp() - stale_seconds
        async with self._db.execute("SELECT * FROM odin_runtime_workers") as cur:
            async for row in cur:
                hb = datetime.fromisoformat(row[3].replace("Z", "+00:00"))
                draining = False
                if len(row) > 6:
                    draining = bool(row[6])
                out.append(
                    {
                        "worker_id": row[0],
                        "capabilities": json.loads(row[1] or "[]"),
                        "concurrency": row[2],
                        "heartbeat_at": row[3],
                        "active_leases": row[4],
                        "stale": hb.timestamp() < cutoff,
                        "draining": draining,
                    }
                )
        return out

    async def start_heartbeat_loop(self, app: Any) -> None:
        import asyncio

        interval = max(10.0, app.settings.runtime_heartbeat_interval_seconds)

        async def _loop() -> None:
            while True:
                leases = 0
                q = getattr(app, "distributed_queue", None)
                if q:
                    leases = q.leases.metrics.get("leases_acquired", 0) - q.leases.metrics.get(
                        "leases_released", 0
                    )
                await self.heartbeat(active_leases=max(0, leases))
                await asyncio.sleep(interval)

        self._task = asyncio.create_task(_loop())


def new_worker_id(prefix: str = "worker") -> str:
    return f"{prefix}-{uuid4().hex[:8]}"

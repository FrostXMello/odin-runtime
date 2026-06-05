"""SQLite durable queue backend."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import aiosqlite

from odin_backend.config import Settings
from odin_backend.core.queueing.queue_backend import QueueBackend
from odin_backend.core.queueing.queue_models import QueueItem, QueueItemStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS odin_queue_items (
    queue_item_id TEXT PRIMARY KEY,
    mission_id TEXT,
    task_id TEXT,
    execution_id TEXT,
    payload TEXT NOT NULL DEFAULT '{}',
    priority INTEGER NOT NULL DEFAULT 50,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    visible_at TEXT NOT NULL,
    lease_expiry TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    dedup_key TEXT,
    worker_id TEXT,
    reason TEXT NOT NULL DEFAULT 'scheduled',
    fencing_token INTEGER,
    lease_epoch INTEGER NOT NULL DEFAULT 0,
    required_capability TEXT
);
CREATE INDEX IF NOT EXISTS idx_odin_queue_visible
    ON odin_queue_items(status, visible_at, priority DESC);
CREATE INDEX IF NOT EXISTS idx_odin_queue_dedup
    ON odin_queue_items(dedup_key, status);
"""


class SQLiteQueueBackend(QueueBackend):
    def __init__(self, settings: Settings) -> None:
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db_path = Path(db_path)
        self._db: aiosqlite.Connection | None = None
        self._max_retries = settings.queue_max_retries
        self._fence_counter = 0

    async def _migrate(self) -> None:
        conn = self._conn()
        for col, ddl in (
            ("fencing_token", "ALTER TABLE odin_queue_items ADD COLUMN fencing_token INTEGER"),
            ("lease_epoch", "ALTER TABLE odin_queue_items ADD COLUMN lease_epoch INTEGER NOT NULL DEFAULT 0"),
            ("required_capability", "ALTER TABLE odin_queue_items ADD COLUMN required_capability TEXT"),
        ):
            try:
                await conn.execute(ddl)
            except Exception:
                pass
        await conn.commit()

    async def connect(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self._db_path))
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(_SCHEMA)
        await self._migrate()
        await self._db.commit()
        logger.info("sqlite_queue_connected", path=str(self._db_path))

    async def disconnect(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    def _conn(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("SQLiteQueueBackend not connected")
        return self._db

    async def enqueue(self, item: QueueItem) -> QueueItem:
        conn = self._conn()
        if item.dedup_key:
            async with conn.execute(
                """SELECT queue_item_id FROM odin_queue_items
                   WHERE dedup_key = ? AND status IN ('pending','visible','leased')
                   LIMIT 1""",
                (item.dedup_key,),
            ) as cur:
                row = await cur.fetchone()
                if row:
                    existing = await self.get(row["queue_item_id"])
                    if existing:
                        return existing

        now = datetime.now(timezone.utc)
        if item.visible_at <= now:
            item.status = QueueItemStatus.VISIBLE
        else:
            item.status = QueueItemStatus.PENDING

        await conn.execute(
            """INSERT INTO odin_queue_items (
                queue_item_id, mission_id, task_id, execution_id, payload, priority,
                status, created_at, visible_at, lease_expiry, retry_count, dedup_key,
                worker_id, reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                item.queue_item_id,
                item.mission_id,
                item.task_id,
                item.execution_id,
                json.dumps(item.payload),
                item.priority,
                item.status.value,
                item.created_at.isoformat(),
                item.visible_at.isoformat(),
                item.lease_expiry.isoformat() if item.lease_expiry else None,
                item.retry_count,
                item.dedup_key,
                item.worker_id,
                item.reason,
            ),
        )
        await conn.commit()
        return item

    async def dequeue(
        self,
        worker_id: str,
        *,
        limit: int = 1,
        lease_seconds: float = 60.0,
    ) -> list[QueueItem]:
        conn = self._conn()
        now = datetime.now(timezone.utc)
        lease_until = now + timedelta(seconds=lease_seconds)
        out: list[QueueItem] = []

        await conn.execute("BEGIN IMMEDIATE")
        try:
            async with conn.execute(
                """SELECT queue_item_id FROM odin_queue_items
                   WHERE status IN ('pending','visible')
                     AND visible_at <= ?
                   ORDER BY priority DESC, created_at ASC
                   LIMIT ?""",
                (now.isoformat(), limit),
            ) as cur:
                rows = await cur.fetchall()

            for row in rows:
                qid = row["queue_item_id"]
                self._fence_counter += 1
                fence = self._fence_counter
                await conn.execute(
                    """UPDATE odin_queue_items
                       SET status='leased', worker_id=?, lease_expiry=?,
                           fencing_token=?, lease_epoch=lease_epoch+1
                       WHERE queue_item_id=? AND status IN ('pending','visible')""",
                    (worker_id, lease_until.isoformat(), fence, qid),
                )
                item = await self.get(qid)
                if item and item.status == QueueItemStatus.LEASED:
                    out.append(item)
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        return out

    async def ack(self, queue_item_id: str, worker_id: str, *, fencing_token: int | None = None) -> bool:
        conn = self._conn()
        if fencing_token is not None:
            cur = await conn.execute(
                """UPDATE odin_queue_items SET status='acked', worker_id=?, lease_expiry=NULL
                   WHERE queue_item_id=? AND worker_id=? AND status='leased'
                     AND fencing_token=?""",
                (worker_id, queue_item_id, worker_id, fencing_token),
            )
        else:
            cur = await conn.execute(
                """UPDATE odin_queue_items SET status='acked', worker_id=?, lease_expiry=NULL
                   WHERE queue_item_id=? AND worker_id=? AND status='leased'""",
                (worker_id, queue_item_id, worker_id),
            )
        await conn.commit()
        return cur.rowcount > 0

    async def nack(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        requeue_delay: float = 0.0,
        reason: str = "nack",
        fencing_token: int | None = None,
    ) -> bool:
        conn = self._conn()
        item = await self.get(queue_item_id)
        if not item or (item.worker_id and item.worker_id != worker_id):
            return False
        if fencing_token is not None and item.fencing_token != fencing_token:
            return False
        retry = item.retry_count + 1
        if retry >= self._max_retries:
            await conn.execute(
                "UPDATE odin_queue_items SET status='deadletter' WHERE queue_item_id=?",
                (queue_item_id,),
            )
            await conn.commit()
            return False
        visible = datetime.now(timezone.utc) + timedelta(seconds=requeue_delay)
        payload = dict(item.payload)
        payload["nack_reason"] = reason
        cur = await conn.execute(
            """UPDATE odin_queue_items
               SET status='visible', worker_id=NULL, lease_expiry=NULL, fencing_token=NULL,
                   retry_count=?, visible_at=?, payload=?
               WHERE queue_item_id=? AND status='leased'""",
            (retry, visible.isoformat(), json.dumps(payload), queue_item_id),
        )
        await conn.commit()
        return cur.rowcount > 0

    async def renew_lease(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        lease_seconds: float,
        fencing_token: int | None = None,
    ) -> bool:
        lease_until = datetime.now(timezone.utc) + timedelta(seconds=lease_seconds)
        conn = self._conn()
        if fencing_token is not None:
            cur = await conn.execute(
                """UPDATE odin_queue_items SET lease_expiry=?
                   WHERE queue_item_id=? AND worker_id=? AND status='leased'
                     AND fencing_token=?""",
                (lease_until.isoformat(), queue_item_id, worker_id, fencing_token),
            )
        else:
            cur = await conn.execute(
                """UPDATE odin_queue_items SET lease_expiry=?
                   WHERE queue_item_id=? AND worker_id=? AND status='leased'""",
                (lease_until.isoformat(), queue_item_id, worker_id),
            )
        await conn.commit()
        return cur.rowcount > 0

    async def requeue_expired(self) -> int:
        conn = self._conn()
        now = datetime.now(timezone.utc).isoformat()
        cur = await conn.execute(
            """UPDATE odin_queue_items
               SET status='visible', worker_id=NULL, lease_expiry=NULL, fencing_token=NULL,
                   retry_count=retry_count+1
               WHERE status='leased' AND lease_expiry IS NOT NULL AND lease_expiry <= ?""",
            (now,),
        )
        await conn.commit()
        return cur.rowcount

    async def stats(self) -> dict[str, Any]:
        conn = self._conn()
        by_status: dict[str, int] = {}
        async with conn.execute(
            "SELECT status, COUNT(*) AS c FROM odin_queue_items GROUP BY status"
        ) as cur:
            async for row in cur:
                by_status[row["status"]] = row["c"]
        total = sum(by_status.values())
        return {"total": total, "by_status": by_status}

    async def get(self, queue_item_id: str) -> QueueItem | None:
        conn = self._conn()
        async with conn.execute(
            "SELECT * FROM odin_queue_items WHERE queue_item_id=?",
            (queue_item_id,),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        return QueueItem(
            queue_item_id=row["queue_item_id"],
            mission_id=row["mission_id"],
            task_id=row["task_id"],
            execution_id=row["execution_id"],
            payload=json.loads(row["payload"] or "{}"),
            priority=int(row["priority"]),
            status=QueueItemStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            visible_at=datetime.fromisoformat(row["visible_at"].replace("Z", "+00:00")),
            lease_expiry=datetime.fromisoformat(row["lease_expiry"].replace("Z", "+00:00"))
            if row["lease_expiry"]
            else None,
            retry_count=int(row["retry_count"]),
            dedup_key=row["dedup_key"],
            worker_id=row["worker_id"],
            reason=row["reason"] or "scheduled",
            fencing_token=int(row["fencing_token"]) if row["fencing_token"] is not None else None,
            lease_epoch=int(row["lease_epoch"] or 0) if "lease_epoch" in row.keys() else 0,
            required_capability=row["required_capability"] if "required_capability" in row.keys() else None,
        )

    async def mark_deadletter(self, queue_item_id: str, *, reason: str) -> None:
        conn = self._conn()
        await conn.execute(
            "UPDATE odin_queue_items SET status='deadletter' WHERE queue_item_id=?",
            (queue_item_id,),
        )
        await conn.commit()

    async def list_deadletter(self, *, limit: int = 50) -> list[QueueItem]:
        conn = self._conn()
        out: list[QueueItem] = []
        async with conn.execute(
            """SELECT queue_item_id FROM odin_queue_items
               WHERE status='deadletter' ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ) as cur:
            async for row in cur:
                item = await self.get(row["queue_item_id"])
                if item:
                    out.append(item)
        return out

    async def replay_item(self, queue_item_id: str) -> QueueItem | None:
        item = await self.get(queue_item_id)
        if not item:
            return None
        new_item = QueueItem(
            queue_item_id=str(uuid4()),
            mission_id=item.mission_id,
            task_id=item.task_id,
            execution_id=item.execution_id,
            payload={**item.payload, "replayed_from": queue_item_id},
            priority=item.priority,
            dedup_key=item.dedup_key,
            reason="replay",
        )
        return await self.enqueue(new_item)

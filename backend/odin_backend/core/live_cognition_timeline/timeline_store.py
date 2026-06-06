"""SQLite cognition timeline registry (Prompt 60)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

MAX_EVENTS = 500


class CognitionTimelineStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS cognition_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT,
                payload TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def append(self, *, kind: str, payload: dict) -> int:
        cur = self._conn.execute(
            "INSERT INTO cognition_events (kind, payload) VALUES (?, ?)",
            (kind[:60], json.dumps(payload)),
        )
        count = self._conn.execute("SELECT COUNT(*) FROM cognition_events").fetchone()[0]
        if count > MAX_EVENTS:
            self._conn.execute(
                """DELETE FROM cognition_events WHERE event_id NOT IN (
                    SELECT event_id FROM cognition_events ORDER BY event_id DESC LIMIT ?
                )""",
                (MAX_EVENTS,),
            )
        self._conn.commit()
        return cur.lastrowid or 0

    def events(self, *, limit: int = 50) -> list[dict]:
        rows = self._conn.execute(
            "SELECT event_id, kind, payload FROM cognition_events ORDER BY event_id DESC LIMIT ?",
            (min(limit, MAX_EVENTS),),
        ).fetchall()
        return [{"event_id": r[0], "kind": r[1], **json.loads(r[2])} for r in rows]

"""SQLite collaborative operator session registry (Prompt 62)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

MAX_SESSIONS = 500


class OperatorSessionStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS operator_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator_id TEXT,
                role TEXT,
                payload TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def create(self, *, operator_id: str, role: str, payload: dict[str, Any]) -> int:
        cur = self._conn.execute(
            "INSERT INTO operator_sessions (operator_id, role, payload) VALUES (?, ?, ?)",
            (operator_id[:80], role[:40], json.dumps(payload)),
        )
        count = self._conn.execute("SELECT COUNT(*) FROM operator_sessions").fetchone()[0]
        if count > MAX_SESSIONS:
            self._conn.execute(
                """DELETE FROM operator_sessions WHERE session_id NOT IN (
                    SELECT session_id FROM operator_sessions ORDER BY session_id DESC LIMIT ?
                )""",
                (MAX_SESSIONS,),
            )
        self._conn.commit()
        return cur.lastrowid or 0

    def sessions(self, *, limit: int = 50) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT session_id, operator_id, role, payload FROM operator_sessions ORDER BY session_id DESC LIMIT ?",
            (min(limit, MAX_SESSIONS),),
        ).fetchall()
        return [{"session_id": r[0], "operator_id": r[1], "role": r[2], **json.loads(r[3])} for r in rows]

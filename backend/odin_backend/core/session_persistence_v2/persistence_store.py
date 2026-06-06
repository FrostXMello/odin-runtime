"""SQLite session persistence registry (Prompt 64)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

MAX_CHECKPOINTS = 200


class SessionPersistenceStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS session_checkpoints (
                checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                payload TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def add_checkpoint(self, *, label: str, payload: dict[str, Any]) -> int:
        cur = self._conn.execute(
            "INSERT INTO session_checkpoints (label, payload) VALUES (?, ?)",
            (label[:80], json.dumps(payload)),
        )
        count = self._conn.execute("SELECT COUNT(*) FROM session_checkpoints").fetchone()[0]
        if count > MAX_CHECKPOINTS:
            self._conn.execute(
                """DELETE FROM session_checkpoints WHERE checkpoint_id NOT IN (
                    SELECT checkpoint_id FROM session_checkpoints ORDER BY checkpoint_id DESC LIMIT ?
                )""",
                (MAX_CHECKPOINTS,),
            )
        self._conn.commit()
        return cur.lastrowid or 0

    def compact(self) -> int:
        before = self._conn.execute("SELECT COUNT(*) FROM session_checkpoints").fetchone()[0]
        self._conn.execute("VACUUM")
        self._conn.commit()
        return before

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM session_checkpoints").fetchone()[0]

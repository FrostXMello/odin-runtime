"""SQLite deferred cognition store (Prompt 53)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any


class DeferredCognitionStore:
    def __init__(self, db_path: Path) -> None:
        self._path = db_path
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS deferred_reasoning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thought TEXT,
                chain TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def defer(self, *, thought: str, chain: list[str] | None = None) -> int:
        cur = self._conn.execute(
            "INSERT INTO deferred_reasoning (thought, chain) VALUES (?, ?)",
            (thought[:500], json.dumps(chain or [])),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def restore_all(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT id, thought, chain FROM deferred_reasoning ORDER BY id").fetchall()
        self._conn.execute("DELETE FROM deferred_reasoning")
        self._conn.commit()
        return [{"id": r[0], "thought": r[1], "chain": json.loads(r[2] or "[]")} for r in rows]

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM deferred_reasoning").fetchone()[0])

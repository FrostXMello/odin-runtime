"""SQLite workspace session registry (Prompt 54)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any


class WorkspaceSessionStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS workspace_sessions (
                session_id TEXT PRIMARY KEY,
                payload TEXT,
                updated_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def save(self, *, session_id: str, payload: dict) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO workspace_sessions (session_id, payload) VALUES (?, ?)",
            (session_id[:80], json.dumps(payload)),
        )
        self._conn.commit()

    def load(self, *, session_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT payload FROM workspace_sessions WHERE session_id = ?", (session_id[:80],)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def latest(self) -> dict | None:
        row = self._conn.execute(
            "SELECT session_id, payload FROM workspace_sessions ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        return {"session_id": row[0], **json.loads(row[1])}

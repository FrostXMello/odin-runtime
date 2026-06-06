"""SQLite execution registry (Prompt 57)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

MAX_CHAINS = 250


class ExecutionStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS execution_chains (
                chain_id TEXT PRIMARY KEY,
                payload TEXT,
                success INTEGER DEFAULT 0,
                updated_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def save(self, *, chain_id: str, payload: dict, success: bool = False) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO execution_chains (chain_id, payload, success) VALUES (?, ?, ?)",
            (chain_id[:80], json.dumps(payload), 1 if success else 0),
        )
        self._compress()
        self._conn.commit()

    def load(self, *, chain_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT payload, success FROM execution_chains WHERE chain_id = ?", (chain_id[:80],)
        ).fetchone()
        if not row:
            return None
        return {"chain_id": chain_id, **json.loads(row[0]), "success": bool(row[1])}

    def successful_patterns(self, *, limit: int = 10) -> list[dict]:
        rows = self._conn.execute(
            "SELECT chain_id, payload FROM execution_chains WHERE success=1 ORDER BY updated_at DESC LIMIT ?",
            (min(limit, 20),),
        ).fetchall()
        return [{"chain_id": r[0], **json.loads(r[1])} for r in rows]

    def _compress(self) -> None:
        count = self._conn.execute("SELECT COUNT(*) FROM execution_chains").fetchone()[0]
        if count > MAX_CHAINS:
            self._conn.execute(
                """DELETE FROM execution_chains WHERE chain_id NOT IN (
                    SELECT chain_id FROM execution_chains ORDER BY updated_at DESC LIMIT ?
                )""",
                (MAX_CHAINS,),
            )

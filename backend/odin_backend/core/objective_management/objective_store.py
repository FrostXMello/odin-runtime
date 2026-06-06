"""SQLite objective registry (Prompt 55)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

MAX_OBJECTIVES = 200


class ObjectiveStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS objectives (
                objective_id TEXT PRIMARY KEY,
                payload TEXT,
                progress REAL DEFAULT 0,
                updated_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def save(self, *, objective_id: str, payload: dict, progress: float = 0) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO objectives (objective_id, payload, progress) VALUES (?, ?, ?)",
            (objective_id[:80], json.dumps(payload), min(1.0, max(0.0, progress))),
        )
        self._compress()
        self._conn.commit()

    def load(self, *, objective_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT payload, progress FROM objectives WHERE objective_id = ?", (objective_id[:80],)
        ).fetchone()
        if not row:
            return None
        return {"objective_id": objective_id, **json.loads(row[0]), "progress": row[1]}

    def list_active(self, *, limit: int = 50) -> list[dict]:
        rows = self._conn.execute(
            "SELECT objective_id, payload, progress FROM objectives ORDER BY updated_at DESC LIMIT ?",
            (min(limit, MAX_OBJECTIVES),),
        ).fetchall()
        out = []
        for oid, payload, progress in rows:
            out.append({"objective_id": oid, **json.loads(payload), "progress": progress})
        return out

    def _compress(self) -> None:
        count = self._conn.execute("SELECT COUNT(*) FROM objectives").fetchone()[0]
        if count > MAX_OBJECTIVES:
            self._conn.execute(
                """DELETE FROM objectives WHERE objective_id NOT IN (
                    SELECT objective_id FROM objectives ORDER BY updated_at DESC LIMIT ?
                )""",
                (MAX_OBJECTIVES,),
            )

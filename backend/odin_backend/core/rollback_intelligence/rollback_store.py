"""SQLite rollback registry (Prompt 61)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

MAX_NODES = 600


class RollbackStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS rollback_nodes (
                node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                confidence REAL,
                payload TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def add_node(self, *, label: str, confidence: float, payload: dict) -> int:
        cur = self._conn.execute(
            "INSERT INTO rollback_nodes (label, confidence, payload) VALUES (?, ?, ?)",
            (label[:80], confidence, json.dumps(payload)),
        )
        count = self._conn.execute("SELECT COUNT(*) FROM rollback_nodes").fetchone()[0]
        if count > MAX_NODES:
            self._conn.execute(
                """DELETE FROM rollback_nodes WHERE node_id NOT IN (
                    SELECT node_id FROM rollback_nodes ORDER BY node_id DESC LIMIT ?
                )""",
                (MAX_NODES,),
            )
        self._conn.commit()
        return cur.lastrowid or 0

    def nodes(self, *, limit: int = 50) -> list[dict]:
        rows = self._conn.execute(
            "SELECT node_id, label, confidence, payload FROM rollback_nodes ORDER BY node_id DESC LIMIT ?",
            (min(limit, MAX_NODES),),
        ).fetchall()
        return [{"node_id": r[0], "label": r[1], "confidence": r[2], **json.loads(r[3])} for r in rows]

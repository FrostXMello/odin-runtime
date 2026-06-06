"""SQLite mission graph registry (Prompt 56)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

MAX_NODES = 300


class MissionGraphStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS mission_nodes (
                node_id TEXT PRIMARY KEY,
                payload TEXT,
                updated_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS mission_edges (
                src TEXT, dst TEXT,
                PRIMARY KEY (src, dst)
            )"""
        )
        self._conn.commit()

    def add_node(self, *, node_id: str, payload: dict) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO mission_nodes (node_id, payload) VALUES (?, ?)",
            (node_id[:80], json.dumps(payload)),
        )
        self._compress()
        self._conn.commit()

    def link(self, *, src: str, dst: str) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO mission_edges (src, dst) VALUES (?, ?)",
            (src[:80], dst[:80]),
        )
        self._conn.commit()

    def nodes(self, *, limit: int = 50) -> list[dict]:
        rows = self._conn.execute(
            "SELECT node_id, payload FROM mission_nodes ORDER BY updated_at DESC LIMIT ?",
            (min(limit, MAX_NODES),),
        ).fetchall()
        return [{"node_id": r[0], **json.loads(r[1])} for r in rows]

    def edges(self) -> list[dict]:
        rows = self._conn.execute("SELECT src, dst FROM mission_edges LIMIT 200").fetchall()
        return [{"src": r[0], "dst": r[1]} for r in rows]

    def _compress(self) -> None:
        count = self._conn.execute("SELECT COUNT(*) FROM mission_nodes").fetchone()[0]
        if count > MAX_NODES:
            self._conn.execute(
                """DELETE FROM mission_nodes WHERE node_id NOT IN (
                    SELECT node_id FROM mission_nodes ORDER BY updated_at DESC LIMIT ?
                )""",
                (MAX_NODES,),
            )

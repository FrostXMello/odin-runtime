"""SQLite execution DAG registry (Prompt 58)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

MAX_NODES = 400


class ExecutionDagStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS dag_nodes (
                node_id TEXT PRIMARY KEY,
                payload TEXT,
                updated_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS dag_edges (
                src TEXT, dst TEXT, PRIMARY KEY (src, dst)
            )"""
        )
        self._conn.commit()

    def add_node(self, *, node_id: str, payload: dict) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO dag_nodes (node_id, payload) VALUES (?, ?)",
            (node_id[:80], json.dumps(payload)),
        )
        count = self._conn.execute("SELECT COUNT(*) FROM dag_nodes").fetchone()[0]
        if count > MAX_NODES:
            self._conn.execute(
                """DELETE FROM dag_nodes WHERE node_id NOT IN (
                    SELECT node_id FROM dag_nodes ORDER BY updated_at DESC LIMIT ?
                )""",
                (MAX_NODES,),
            )
        self._conn.commit()

    def add_edge(self, *, src: str, dst: str) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO dag_edges (src, dst) VALUES (?, ?)",
            (src[:80], dst[:80]),
        )
        self._conn.commit()

    def topology(self) -> dict:
        nodes = [{"node_id": r[0], **json.loads(r[1])} for r in self._conn.execute(
            "SELECT node_id, payload FROM dag_nodes ORDER BY updated_at DESC LIMIT 100"
        ).fetchall()]
        edges = [{"src": r[0], "dst": r[1]} for r in self._conn.execute(
            "SELECT src, dst FROM dag_edges LIMIT 200"
        ).fetchall()]
        return {"nodes": nodes, "edges": edges}

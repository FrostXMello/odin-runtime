"""SQLite-backed persistent agent store (Prompt 52)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any


class AgentStore:
    def __init__(self, db_path: Path) -> None:
        self._path = db_path
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS persistent_agents (
                agent_id TEXT PRIMARY KEY,
                specialization TEXT,
                memory_summary TEXT,
                active_objectives TEXT,
                workload_score REAL DEFAULT 0.0
            )"""
        )
        self._conn.commit()

    def upsert(self, agent: dict[str, Any]) -> None:
        self._conn.execute(
            """INSERT OR REPLACE INTO persistent_agents
               (agent_id, specialization, memory_summary, active_objectives, workload_score)
               VALUES (?, ?, ?, ?, ?)""",
            (
                agent["agent_id"],
                agent.get("specialization", ""),
                agent.get("memory_summary", ""),
                json.dumps(agent.get("active_objectives", [])),
                float(agent.get("workload_score", 0.0)),
            ),
        )
        self._conn.commit()

    def list_agents(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT agent_id, specialization, memory_summary, active_objectives, workload_score FROM persistent_agents").fetchall()
        return [
            {
                "agent_id": r[0],
                "specialization": r[1],
                "memory_summary": r[2],
                "active_objectives": json.loads(r[3] or "[]"),
                "workload_score": r[4],
            }
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()

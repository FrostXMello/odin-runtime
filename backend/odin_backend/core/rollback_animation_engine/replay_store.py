"""SQLite rollback animation replay registry (Prompt 63)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

MAX_FRAMES = 500


class RollbackAnimationStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS animation_frames (
                frame_id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                payload TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def add_frame(self, *, label: str, payload: dict[str, Any]) -> int:
        cur = self._conn.execute(
            "INSERT INTO animation_frames (label, payload) VALUES (?, ?)",
            (label[:80], json.dumps(payload)),
        )
        count = self._conn.execute("SELECT COUNT(*) FROM animation_frames").fetchone()[0]
        if count > MAX_FRAMES:
            self._conn.execute(
                """DELETE FROM animation_frames WHERE frame_id NOT IN (
                    SELECT frame_id FROM animation_frames ORDER BY frame_id DESC LIMIT ?
                )""",
                (MAX_FRAMES,),
            )
        self._conn.commit()
        return cur.lastrowid or 0

    def frames(self, *, limit: int = 50) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT frame_id, label, payload FROM animation_frames ORDER BY frame_id DESC LIMIT ?",
            (min(limit, MAX_FRAMES),),
        ).fetchall()
        return [{"frame_id": r[0], "label": r[1], **json.loads(r[2])} for r in rows]

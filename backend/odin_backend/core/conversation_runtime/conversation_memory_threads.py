"""Persistent conversation threads."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

class ThreadStore:
    def __init__(self) -> None:
        self._threads: dict[str, list[dict]] = {}

    def append(self, thread_id: str, role: str, content: str) -> dict[str, Any]:
        tid = thread_id or str(uuid4())
        self._threads.setdefault(tid, []).append({"role": role, "content": content[:4000]})
        return {"thread_id": tid, "count": len(self._threads[tid])}

    def restore(self, thread_id: str) -> dict[str, Any]:
        msgs = self._threads.get(thread_id, [])
        return {"thread_id": thread_id, "messages": msgs, "restored": bool(msgs)}

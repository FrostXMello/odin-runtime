from __future__ import annotations
from uuid import uuid4

class ThreadStore:
    def __init__(self) -> None:
        self._threads: dict[str, list[dict]] = {}

    def append(self, thread_id: str, msg: dict) -> str:
        tid = thread_id or str(uuid4())
        self._threads.setdefault(tid, []).append(msg)
        return tid

    def restore(self, thread_id: str) -> dict:
        msgs = self._threads.get(thread_id, [])
        return {"thread_id": thread_id, "messages": msgs, "restored": bool(msgs)}

"""Persistent memory threads orchestrator."""
from __future__ import annotations
import time
from typing import Any
from uuid import uuid4

from odin_backend.core.memory_threads.conversational_threads import conv_thread
from odin_backend.core.memory_threads.project_threads import project_thread
from odin_backend.core.memory_threads.semantic_threads import semantic
from odin_backend.core.memory_threads.thread_decay import decay
from odin_backend.core.memory_threads.thread_linking import link
from odin_backend.core.memory_threads.thread_prioritization import prioritize


class MemoryThreadsRuntime:
    MAX_THREADS = 64

    def __init__(self, app: Any) -> None:
        self._app = app
        self._threads: dict[str, dict] = {}

    async def activate(self, *, topic: str, project: str = "", thread_id: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "memory_threads_enabled", False):
            return {"accepted": False, "reason": "memory_threads_disabled"}
        tid = thread_id or str(uuid4())
        if len(self._threads) >= self.MAX_THREADS:
            oldest = min(self._threads.values(), key=lambda t: t.get("created_at", 0))
            self._threads = {k: v for k, v in self._threads.items() if v != oldest}
        meta = {**semantic(topic=topic), **project_thread(project=project or topic), "weight": 1.0, "created_at": time.time()}
        self._threads[tid] = meta
        self._emit("memory_thread_activated", {"thread_id": tid, "topic": topic[:80]})
        return {"accepted": True, "thread_id": tid, "meta": meta}

    async def recall(self, *, limit: int = 8) -> dict[str, Any]:
        threads = prioritize(list(self._threads.values()))
        return {"accepted": True, "threads": threads[:limit]}

    async def link_threads(self, *, a: str, b: str) -> dict[str, Any]:
        return {"accepted": True, "link": link(a, b)}

    def snapshot(self) -> dict[str, Any]:
        return {"count": len(self._threads), "max": self.MAX_THREADS}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="memory_threads")

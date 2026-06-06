"""Unified memory fabric (Prompt 48)."""
from __future__ import annotations
from typing import Any
import json
from pathlib import Path

from odin_backend.core.memory_fabric.attention_index import index
from odin_backend.core.memory_fabric.cross_runtime_memory import link_runtimes
from odin_backend.core.memory_fabric.episodic_threads import EpisodicThreads
from odin_backend.core.memory_fabric.memory_rehydration import rehydrate
from odin_backend.core.memory_fabric.relevance_decay import decay
from odin_backend.core.memory_fabric.semantic_continuity import stitch
from odin_backend.core.memory_fabric.temporal_linking import link_events


class MemoryFabricRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._threads = EpisodicThreads()
        self._path = "./data/memory_fabric.json"

    async def link(self, *, topic: str, prior: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "memory_fabric_enabled", False):
            return {"accepted": False, "reason": "memory_fabric_disabled"}
        thread = self._threads.add(topic)
        links = await link_runtimes(self._app)
        cont = stitch(prior=prior, current=topic) if prior else {}
        temporal = link_events([prior, topic] if prior else [topic])
        self._emit("memory_fabric_linked", {"topic": topic[:40], "links": links.get("links", [])})
        graph = {"threads": [thread], "temporal": temporal, "continuity": cont}
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        Path(self._path).write_text(json.dumps(graph), encoding="utf-8")
        return {"accepted": True, "thread": thread, "links": links, "graph": graph}

    async def recall(self, *, query: str = "") -> dict[str, Any]:
        restored = rehydrate(path=self._path)
        items = index([query] if query else ["session"], weight=decay(age_hours=1))
        if hasattr(self._app, "memory_threads"):
            await self._app.memory_threads.recall()
        return {"accepted": True, "restored": restored, "attention_index": items}

    def snapshot(self) -> dict[str, Any]:
        return {"threads": len(self._threads._threads)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="memory_fabric")

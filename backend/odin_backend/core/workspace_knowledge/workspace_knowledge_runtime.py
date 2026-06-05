"""Knowledge workspace orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.workspace_knowledge.document_memory import DocumentMemory
from odin_backend.core.workspace_knowledge.meeting_memory import MeetingMemory
from odin_backend.core.workspace_knowledge.note_linking import NoteLinking
from odin_backend.core.workspace_knowledge.pdf_ingestion import ingest_pdf
from odin_backend.core.workspace_knowledge.personal_knowledge_graph import PersonalKnowledgeGraph
from odin_backend.core.workspace_knowledge.semantic_workspace import SemanticWorkspace
from odin_backend.core.workspace_knowledge.timeline_memory import build_timeline


class WorkspaceKnowledgeRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._docs = DocumentMemory()
        self._semantic = SemanticWorkspace()
        self._graph = PersonalKnowledgeGraph()
        self._links = NoteLinking()
        self._meetings = MeetingMemory()
        self._timeline: list[dict[str, Any]] = []

    async def ingest(self, *, title: str, content: str, kind: str = "note") -> dict[str, Any]:
        if not getattr(self._app.settings, "workspace_knowledge_enabled", False):
            return {"accepted": False, "reason": "workspace_knowledge_disabled"}
        doc = self._docs.store(title=title, content=content, kind=kind)
        chunk = self._semantic.index(text=content, metadata={"title": title, "kind": kind})
        node = self._graph.add_node(title, label=title, kind=kind)
        self._timeline.append({"at": doc.get("title"), "kind": kind, "title": title})
        self._emit("knowledge_cluster_created", {"title": title, "node": node["id"]})
        if hasattr(self._app, "vector_memory"):
            await self._app.vector_memory.ingest(content, metadata={"title": title, "kind": kind})
        return {"accepted": True, "document": doc, "chunk": chunk}

    async def ingest_pdf(self, *, filename: str, text: str) -> dict[str, Any]:
        meta = ingest_pdf(filename=filename, text=text)
        return await self.ingest(title=filename, content=text, kind="pdf")

    async def search(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        return self._semantic.search(query, limit=limit)

    def timeline(self) -> list[dict[str, Any]]:
        return build_timeline(self._timeline)

    def snapshot(self) -> dict[str, Any]:
        return {"documents": len(self._docs.list_all()), "graph": self._graph.snapshot()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workspace_knowledge")

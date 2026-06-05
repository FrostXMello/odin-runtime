"""ChromaDB semantic store with in-memory fallback."""

from typing import Any
from uuid import uuid4

from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class SemanticStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Any = None
        self._collection: Any = None
        self._fallback: list[dict[str, Any]] = []

    async def connect(self) -> None:
        try:
            import chromadb

            self._settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self._settings.chroma_persist_dir))
            self._collection = self._client.get_or_create_collection(
                name="odin_semantic",
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("chroma_connected", path=str(self._settings.chroma_persist_dir))
        except Exception as exc:
            logger.warning("chroma_fallback_inmemory", error=str(exc))
            self._collection = None

    async def disconnect(self) -> None:
        self._client = None
        self._collection = None

    async def store(
        self, content: str, *, category: str = "general", metadata: dict[str, Any] | None = None
    ) -> str:
        memory_id = str(uuid4())
        meta = {"category": category, **(metadata or {})}

        if self._collection is not None:
            try:
                self._collection.add(
                    ids=[memory_id],
                    documents=[content],
                    metadatas=[meta],
                )
                return memory_id
            except Exception as exc:
                logger.warning("chroma_store_fallback", error=str(exc))
                self._collection = None

        self._fallback.append({"id": memory_id, "content": content, "metadata": meta})
        return memory_id

    async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if self._collection is not None:
            try:
                results = self._collection.query(query_texts=[query], n_results=limit)
                docs = results.get("documents", [[]])[0]
                ids = results.get("ids", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                return [
                    {"id": i, "content": d, "metadata": m}
                    for i, d, m in zip(ids, docs, metas)
                ]
            except Exception as exc:
                logger.warning("chroma_search_error", error=str(exc))

        # Fallback: simple keyword match
        q = query.lower()
        matched = [
            {"id": e["id"], "content": e["content"], "metadata": e["metadata"]}
            for e in self._fallback
            if q in e["content"].lower()
        ]
        return matched[:limit]

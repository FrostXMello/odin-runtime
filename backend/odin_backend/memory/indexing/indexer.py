"""Indexes episodic entries for faster retrieval."""

from odin_backend.memory.episodic.store import EpisodicEntry, EpisodicStore


class MemoryIndexer:
    def __init__(self, episodic: EpisodicStore) -> None:
        self._episodic = episodic
        self._by_workflow: dict[str, list[str]] = {}

    def index_entry(self, entry: EpisodicEntry) -> None:
        if entry.workflow_id:
            self._by_workflow.setdefault(entry.workflow_id, []).append(entry.id)

    async def get_workflow_entries(self, workflow_id: str) -> list[EpisodicEntry]:
        return await self._episodic.query(workflow_id=workflow_id)

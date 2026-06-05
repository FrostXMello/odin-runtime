"""Desktop graph model — windows, apps, tabs, terminals as entities."""

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class DesktopEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    entity_type: str  # window | app | tab | terminal | file | workflow
    label: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DesktopGraph(BaseModel):
    entities: list[DesktopEntity] = Field(default_factory=list)
    edges: list[dict[str, str]] = Field(default_factory=list)

    def add_entity(self, entity_type: str, label: str, **meta: Any) -> DesktopEntity:
        ent = DesktopEntity(entity_type=entity_type, label=label, metadata=meta)
        self.entities.append(ent)
        return ent

    def link(self, source_id: str, target_id: str, relation: str) -> None:
        self.edges.append({"source": source_id, "target": target_id, "relation": relation})

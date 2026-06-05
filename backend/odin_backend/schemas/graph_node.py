"""Knowledge graph node — strict schema."""

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeGraphNode(BaseModel):
    id: str
    entity: str
    relationships: list[tuple[str, str, str]] = Field(
        default_factory=list,
        description="(relation, target_id, target_entity) tuples",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

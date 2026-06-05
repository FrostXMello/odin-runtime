"""Memory summarization — daily, workflow, project compression."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MemorySummary(BaseModel):
    summary_type: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


def summarize_entries(entries: list[str], max_sentences: int = 8) -> str:
    combined = " ".join(entries)
    sentences = [s.strip() for s in combined.replace("\n", " ").split(".") if s.strip()]
    return ". ".join(sentences[:max_sentences]) + ("." if sentences else "")


class MemorySummarizer:
    async def summarize_workflow(self, objective: str, step_summaries: list[str]) -> MemorySummary:
        content = summarize_entries([objective, *step_summaries], max_sentences=6)
        return MemorySummary(summary_type="workflow", content=content, metadata={"steps": len(step_summaries)})

    async def summarize_project(self, project: str, memories: list[str]) -> MemorySummary:
        content = summarize_entries(memories, max_sentences=10)
        return MemorySummary(
            summary_type="project",
            content=f"[{project}] {content}",
            metadata={"project": project, "count": len(memories)},
        )

    async def daily_summary(self, events: list[str]) -> MemorySummary:
        content = summarize_entries(events, max_sentences=12)
        return MemorySummary(summary_type="daily", content=content, metadata={"events": len(events)})

"""Project-based memory clustering."""

from enum import StrEnum
from typing import Any


class MemoryProject(StrEnum):
    PROJECT_ODIN = "PROJECT_ODIN"
    DYNACI_STUDIOS = "DYNACI_STUDIOS"
    FINANCE = "FINANCE"
    COLLEGE = "COLLEGE"
    RESEARCH = "RESEARCH"
    GENERAL = "GENERAL"


PROJECT_KEYWORDS: dict[MemoryProject, list[str]] = {
    MemoryProject.PROJECT_ODIN: ["odin", "orchestrator", "agent", "workflow", "mimir"],
    MemoryProject.DYNACI_STUDIOS: ["dynaci", "studio", "client", "production"],
    MemoryProject.FINANCE: ["stock", "crypto", "market", "portfolio", "fafnir"],
    MemoryProject.COLLEGE: ["college", "course", "assignment", "exam"],
    MemoryProject.RESEARCH: ["research", "paper", "arxiv", "study"],
}


def infer_project(content: str, metadata: dict[str, Any] | None = None) -> MemoryProject:
    if metadata and metadata.get("project"):
        try:
            return MemoryProject(metadata["project"])
        except ValueError:
            pass
    lower = content.lower()
    for project, keywords in PROJECT_KEYWORDS.items():
        if any(k in lower for k in keywords):
            return project
    return MemoryProject.GENERAL

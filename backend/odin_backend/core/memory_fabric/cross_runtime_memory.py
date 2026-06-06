from __future__ import annotations
from typing import Any


async def link_runtimes(app: Any) -> dict:
    links = []
    if hasattr(app, "memory_threads"):
        links.append("memory_threads")
    if hasattr(app, "project_memory"):
        links.append("project_memory")
    return {"links": links}

from __future__ import annotations

from typing import Any


def link_threads(*, threads: list[dict]) -> dict[str, Any]:
    projects = {t.get("project") for t in threads}
    return {"threads": len(threads), "projects": len(projects)}

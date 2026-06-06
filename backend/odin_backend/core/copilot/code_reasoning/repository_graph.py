from __future__ import annotations

from typing import Any


def build_repository_graph(*, repo: str, files: list[str]) -> dict[str, Any]:
    return {"repo": repo, "nodes": len(files), "edges": max(0, len(files) - 1), "files": files[:20]}

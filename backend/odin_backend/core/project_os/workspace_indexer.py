"""Workspace indexing."""

from __future__ import annotations

from typing import Any


def index_workspace(*, root: str, files: list[str] | None = None) -> dict[str, Any]:
    files = files or []
    return {"root": root, "file_count": len(files), "indexed": files[:100]}

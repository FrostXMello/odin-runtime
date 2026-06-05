"""Repository-aware codebase context."""

from __future__ import annotations

from typing import Any


def build_codebase_context(*, repo_path: str, languages: list[str] | None = None) -> dict[str, Any]:
    return {
        "repo_path": repo_path,
        "languages": languages or ["python", "typescript"],
        "structure_hint": "src/, tests/, docs/",
    }

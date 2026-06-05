"""Repository intelligence summaries."""

from __future__ import annotations

from typing import Any


def summarize_repo(*, path: str, commits: list[str] | None = None) -> dict[str, Any]:
    commits = commits or []
    return {
        "path": path,
        "commit_count": len(commits),
        "recent": commits[-3:],
        "summary": f"Repository at {path} with {len(commits)} tracked commits",
    }

"""Git observer (read-only)."""

from __future__ import annotations

from typing import Any


def summarize_commits(commits: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(commits),
        "messages": [c.get("message", "")[:80] for c in commits[-5:]],
        "write_allowed": False,
    }

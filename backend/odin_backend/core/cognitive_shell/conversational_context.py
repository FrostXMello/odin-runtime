"""Conversational context routing for shell."""

from __future__ import annotations

from typing import Any


def build_context(*, workspace: dict | None = None, memory_threads: list | None = None) -> dict[str, Any]:
    ws = workspace or {}
    threads = memory_threads or []
    return {
        "workspace_app": ws.get("active_app", "unknown"),
        "thread_count": len(threads),
        "threads": threads[:5],
        "continuity_key": ws.get("session_id", "default"),
    }

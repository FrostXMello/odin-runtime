"""Reflect on execution outcomes for retry quality."""

from __future__ import annotations

from typing import Any


def reflect_execution(*, success: bool, error: str | None = None, retries: int = 0) -> dict[str, Any]:
    lesson = "retry_with_smaller_scope" if not success and retries < 2 else "escalate_to_operator"
    if success:
        lesson = "preserve_strategy"
    return {
        "success": success,
        "retries": retries,
        "lesson": lesson,
        "should_retry": not success and retries < 3 and (error or "").find("timeout") >= 0,
    }

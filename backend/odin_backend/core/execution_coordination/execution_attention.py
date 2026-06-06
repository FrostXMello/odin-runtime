from __future__ import annotations

from typing import Any


def focus_execution(*, task: str) -> dict[str, Any]:
    return {"task": task, "attention": "high"}

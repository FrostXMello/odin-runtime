from __future__ import annotations

from typing import Any


def record_workflow(*, action: str) -> dict[str, Any]:
    return {"action": action, "recorded": True}

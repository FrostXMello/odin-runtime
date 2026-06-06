from __future__ import annotations

from typing import Any


def coordinate_agents(*, agents: list[str], task: str) -> dict[str, Any]:
    return {"agents": agents, "task": task, "cooperative": True, "supervised": True}

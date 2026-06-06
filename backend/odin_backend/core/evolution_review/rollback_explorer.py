from __future__ import annotations
from typing import Any


def simulate_rollback(*, target: str) -> dict[str, Any]:
    return {"target": target, "simulated": True, "main_branch_safe": True}

from __future__ import annotations

from typing import Any


def select_strategy(*, root_cause: str, prior_failures: int) -> dict[str, Any]:
    if prior_failures > 2:
        return {"strategy": "escalate_operator", "supervised": True}
    if root_cause == "import_error":
        return {"strategy": "fix_imports", "supervised": True}
    return {"strategy": "isolate_and_patch", "supervised": True}

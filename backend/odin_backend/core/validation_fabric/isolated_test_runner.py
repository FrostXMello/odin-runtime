from __future__ import annotations

from typing import Any


def run_isolated(*, test_pattern: str) -> dict[str, Any]:
    return {"pattern": test_pattern, "isolated": True, "passed": True}

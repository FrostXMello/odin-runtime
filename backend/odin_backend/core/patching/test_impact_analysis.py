from __future__ import annotations

from typing import Any


def analyze_test_impact(*, diff: str) -> dict[str, Any]:
    impacted = diff.count("test_") + diff.count("tests/")
    return {"impacted": impacted, "recommend_run_tests": impacted > 0 or len(diff) > 100}

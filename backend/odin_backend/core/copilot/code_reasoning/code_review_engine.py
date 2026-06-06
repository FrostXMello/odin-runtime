from __future__ import annotations

from typing import Any


def review_code(*, diff: str) -> dict[str, Any]:
    issues = []
    if "TODO" in diff:
        issues.append("contains_todo")
    if len(diff.splitlines()) > 500:
        issues.append("large_diff")
    score = max(0.2, 1.0 - len(issues) * 0.2)
    return {"score": round(score, 3), "issues": issues, "approved": score >= 0.6}

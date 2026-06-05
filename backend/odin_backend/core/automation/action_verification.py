"""Action verification layer for real automation."""

from __future__ import annotations

from typing import Any


def verify_action(*, kind: str, result: dict[str, Any], expected: dict[str, Any] | None = None) -> dict[str, Any]:
    expected = expected or {}
    score = 1.0
    issues: list[str] = []
    if result.get("simulated"):
        return {"verified": True, "score": 1.0, "mode": "simulation", "issues": []}
    if result.get("success") is False:
        score = 0.0
        issues.append("execution_failed")
    if expected.get("dom_hash") and result.get("dom_hash") != expected.get("dom_hash"):
        score -= 0.3
        issues.append("dom_mismatch")
    if expected.get("ocr_text") and expected.get("ocr_text") not in str(result.get("ocr_text", "")):
        score -= 0.2
        issues.append("ocr_mismatch")
    score = max(0.0, min(1.0, score))
    return {"verified": score >= 0.7, "score": score, "issues": issues, "kind": kind}


def click_confidence(*, target_bounds: dict[str, float] | None, hit: bool) -> float:
    if not hit:
        return 0.0
    if not target_bounds:
        return 0.6
    area = target_bounds.get("width", 0) * target_bounds.get("height", 0)
    return min(1.0, 0.5 + area / 10000.0)

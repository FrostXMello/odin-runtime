"""Grade model responses for usefulness and accuracy signals."""

from __future__ import annotations

from typing import Any


def grade_response(*, text: str, expected_keywords: list[str] | None = None) -> dict[str, Any]:
    expected_keywords = expected_keywords or []
    hits = sum(1 for k in expected_keywords if k.lower() in text.lower())
    coverage = hits / max(len(expected_keywords), 1) if expected_keywords else 0.5
    length_ok = 20 <= len(text) <= 8000
    score = round(min(1.0, coverage * 0.7 + (0.3 if length_ok else 0.1)), 3)
    return {"score": score, "keyword_hits": hits, "length_ok": length_ok}

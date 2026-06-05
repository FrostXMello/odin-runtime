"""Hypothesis tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class HypothesisEngine:
    def __init__(self) -> None:
        self._hypotheses: list[dict[str, Any]] = []

    def add(self, *, topic: str, hypothesis: str, confidence: float) -> dict[str, Any]:
        entry = {
            "id": str(uuid4()),
            "topic": topic,
            "hypothesis": hypothesis,
            "confidence": confidence,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._hypotheses.append(entry)
        return entry

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._hypotheses)[-30:]

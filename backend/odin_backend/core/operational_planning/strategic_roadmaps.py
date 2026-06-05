"""Strategic roadmaps."""

from __future__ import annotations

from typing import Any


def build_roadmap(*, goal: str, milestones: int = 4) -> list[dict[str, Any]]:
    return [{"milestone": i + 1, "label": f"{goal}_M{i+1}", "confidence": round(0.9 - i * 0.1, 2)} for i in range(min(milestones, 10))]

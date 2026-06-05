"""Milestone projection."""

from __future__ import annotations

from typing import Any


def project_milestones(roadmap: list[dict]) -> dict[str, Any]:
    avg = sum(m.get("confidence", 0.5) for m in roadmap) / max(len(roadmap), 1)
    return {"milestone_count": len(roadmap), "aggregate_confidence": round(avg, 4)}

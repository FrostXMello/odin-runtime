"""Agent society intelligence helpers."""

from __future__ import annotations

from typing import Any


def evolve_specialist(*, domain: str, success_rate: float) -> dict[str, Any]:
    level = "expert" if success_rate > 0.8 else "journeyman" if success_rate > 0.5 else "novice"
    return {"domain": domain, "level": level, "success_rate": success_rate}


def distill_reasoning(*, patterns: list[str]) -> dict[str, Any]:
    return {"patterns": len(patterns), "distilled": patterns[:3]}


def score_delegation(*, task_complexity: float, agent_fit: float) -> dict[str, Any]:
    score = round(task_complexity * 0.4 + agent_fit * 0.6, 3)
    return {"score": score, "recommended": score > 0.55}


def score_consensus(*, votes: list[float]) -> dict[str, Any]:
    avg = sum(votes) / max(len(votes), 1)
    return {"consensus": round(avg, 3), "unanimous": len(set(round(v, 1) for v in votes)) == 1}


def route_expertise(*, task: str, experts: dict[str, float]) -> dict[str, Any]:
    best = max(experts, key=experts.get) if experts else "generalist"
    return {"task": task, "expert": best, "confidence": experts.get(best, 0.5)}


def collaborative_memory(*, agent_id: str, insight: str) -> dict[str, Any]:
    return {"agent_id": agent_id, "insight": insight[:500], "shared": True}

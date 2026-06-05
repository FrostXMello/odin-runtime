"""Planner feedback from cognitive learning."""

from __future__ import annotations

from typing import Any

from odin_backend.core.planning.learning_profile import PlannerLearningProfile
from odin_backend.core.planning.objectives import ParsedObjective


def build_learning_profile(app: Any | None) -> PlannerLearningProfile:
    profile = PlannerLearningProfile()
    if not app:
        return profile
    exp = getattr(app, "experience_engine", None)
    if exp:
        for kind, stats in exp.strategy_stats().items():
            profile.strategy_success_rate[kind] = float(stats.get("success_rate", 0.5))
            profile.avg_latency_ms = max(profile.avg_latency_ms, float(stats.get("avg_latency_ms", 0)))
        events = getattr(exp, "_events", [])
        if events:
            fails = sum(1 for e in events if not e.get("success"))
            profile.retry_rate = fails / len(events)
    intel = getattr(app, "execution_intelligence", None)
    if intel and hasattr(intel, "capability_scores"):
        for cap, score in intel.capability_scores().items():
            if score.get("failure_rate", 0) > 0.5:
                profile.penalized_capabilities.append(cap)
    retrieval = getattr(app, "memory_retrieval", None)
    if retrieval:
        import asyncio

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
    return profile


def apply_feedback_to_confidence(
    base_confidence: dict[str, float],
    profile: PlannerLearningProfile,
    *,
    strategy_kind: str,
) -> dict[str, float]:
    out = dict(base_confidence)
    rate = profile.strategy_success_rate.get(strategy_kind, 0.5)
    boost = (rate - 0.5) * 0.15
    for k in out:
        out[k] = max(0.05, min(0.99, out[k] + boost))
    if profile.retry_rate > 0.4:
        out["recovery"] = max(0.05, out.get("recovery", 0.7) - 0.1)
    return out


def suggest_strategy_override(
    parsed: ParsedObjective,
    profile: PlannerLearningProfile,
    default_kind: str,
) -> str | None:
    best = profile.best_strategy
    if not best:
        return None
    if profile.strategy_success_rate.get(best, 0) < 0.55:
        return None
    if profile.strategy_success_rate.get(default_kind, 0.5) < profile.strategy_success_rate[best] - 0.15:
        return best
    return None

"""Single optimization cycle runner."""

from __future__ import annotations

from typing import Any


async def run_optimization_cycle(app: Any) -> dict[str, Any]:
    results: dict[str, Any] = {}
    graph = getattr(app, "cognitive_memory", None)
    if graph:
        results["decayed_entities"] = await graph.decay_stale()
    exp = getattr(app, "experience_engine", None)
    if exp:
        results["strategy_stats"] = exp.strategy_stats()
    if exp:
        from odin_backend.core.cognition.improvement.policy_tuner import tune_policies

        results["policy_tuning"] = tune_policies(exp.strategy_stats())
    fail_intel = getattr(app, "failure_intelligence", None)
    if fail_intel:
        report = await fail_intel.analyze()
        results["failure_intelligence"] = report.to_dict()
    obs = getattr(app, "observability", None)
    if obs:
        from odin_backend.core.observability.events import TraceEventKind

        obs.tracer.record(
            TraceEventKind.OPTIMIZATION_CYCLE_COMPLETED,
            message="optimization cycle",
            payload=results,
            component="improvement_loop",
        )
    return results

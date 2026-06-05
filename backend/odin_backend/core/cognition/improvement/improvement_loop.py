"""Continuous improvement loop — metadata and heuristic optimization only."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognition.improvement.optimization_cycles import run_optimization_cycle
from odin_backend.core.cognition.improvement.policy_tuner import tune_policies
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ImprovementLoop:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._cycles = 0

    @property
    def cycle_count(self) -> int:
        return self._cycles

    async def run_cycle(self) -> dict[str, Any]:
        self._cycles += 1
        results = await run_optimization_cycle(self._app)
        results["cycle"] = self._cycles
        logger.info("improvement_cycle_complete", **{k: v for k, v in results.items() if isinstance(v, (int, float, str))})
        return results

    async def recalibrate_confidence(self) -> dict[str, Any]:
        graph = getattr(self._app, "cognitive_memory", None)
        decayed = await graph.decay_stale() if graph else 0
        obs = getattr(self._app, "observability", None)
        if obs:
            from odin_backend.core.observability.events import TraceEventKind

            obs.tracer.record(
                TraceEventKind.CONFIDENCE_RECALIBRATED,
                message=f"decayed {decayed} entities",
                payload={"decayed": decayed},
                component="improvement_loop",
            )
        return {"decayed_entities": decayed}

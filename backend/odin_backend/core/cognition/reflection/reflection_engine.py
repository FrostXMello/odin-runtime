"""Reflection engine with recursion guards and time budgets."""

from __future__ import annotations

import time
from typing import Any

from odin_backend.core.cognition.reflection.contradiction_detection import detect_contradictions
from odin_backend.core.cognition.reflection.plan_revision import revision_prompt
from odin_backend.core.cognition.reflection.reasoning_validation import (
    hallucination_risk_score,
    validate_strategy,
)
from odin_backend.core.cognition.reflection.self_critique import critique_prompt
class ReflectionEngine:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._reflections: dict[str, list[dict[str, Any]]] = {}
        self._active_depth: dict[str, int] = {}

    async def reflect(
        self,
        *,
        plan: str,
        objective: str,
        mission_id: str | None = None,
        depth: int = 0,
    ) -> dict[str, Any]:
        max_depth = getattr(self._app.settings, "reflection_max_depth", 2)
        budget = getattr(self._app.settings, "reflection_time_budget_seconds", 30.0)
        start = time.perf_counter()

        key = mission_id or "global"
        if depth >= max_depth or self._active_depth.get(key, 0) >= max_depth:
            return {"skipped": True, "reason": "max_depth", "depth": depth}
        self._active_depth[key] = self._active_depth.get(key, 0) + 1

        contradictions = detect_contradictions(plan)
        if contradictions:
            self._emit("contradiction_detected", {"count": len(contradictions)}, mission_id=mission_id)

        ctx = await self._app.reasoning_pipeline.build(objective=objective, mission_id=mission_id)
        risk = hallucination_risk_score(plan, grounding_size=len(ctx.get("prompt_block", "")))
        if risk > 0.55:
            self._emit("hallucination_risk", {"score": risk}, mission_id=mission_id)

        intel = getattr(self._app, "execution_intelligence", None)
        cap_stats = intel.capability_scores() if intel else {}
        validation = validate_strategy(plan, cap_stats)

        model = self._app.model_manager.runtime.router.select_model(
            capability=__import__(
                "odin_backend.core.models.model_profiles", fromlist=["ModelCapabilityTag"]
            ).ModelCapabilityTag.REASONING,
        )
        critique = await self._app.model_manager.runtime.infer(
            messages=critique_prompt(plan=plan, objective=objective),
            model=model,
            task_kind="reflection",
            mission_id=mission_id,
        )
        revised = plan
        if depth < max_depth - 1 and (time.perf_counter() - start) < budget:
            revised = await self._app.model_manager.runtime.infer(
                messages=revision_prompt(plan=plan, critique=str(critique)),
                model=model,
                task_kind="reflection",
                mission_id=mission_id,
            )

        confidence_correction = max(0.1, 0.85 - risk - len(contradictions) * 0.05)
        result = {
            "mission_id": mission_id,
            "objective": objective,
            "critique": critique,
            "revised_plan": revised,
            "contradictions": contradictions,
            "hallucination_risk": risk,
            "validation": validation,
            "confidence_correction": confidence_correction,
            "depth": depth,
        }
        if mission_id:
            self._reflections.setdefault(mission_id, []).append(result)
        self._emit("reflection_generated", {"depth": depth, "risk": risk}, mission_id=mission_id)
        self._active_depth[key] = max(0, self._active_depth.get(key, 1) - 1)
        return result

    def get_reflections(self, mission_id: str) -> list[dict[str, Any]]:
        return self._reflections.get(mission_id, [])

    def _emit(self, kind_name: str, payload: dict, *, mission_id: str | None = None) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        if mission_id:
            payload = {**payload, "mission_id": mission_id}
        obs.tracer.record(kind, message=kind_name, payload=payload, component="reflection_engine")

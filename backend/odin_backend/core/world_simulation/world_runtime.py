"""World simulation runtime orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.world_simulation.causal_world_graph import CausalWorldGraph
from odin_backend.core.world_simulation.prediction_engine import PredictionEngine
from odin_backend.core.world_simulation.scenario_planner import plan_scenarios
from odin_backend.core.world_simulation.simulation_engine import SimulationEngine
from odin_backend.core.world_simulation.strategy_projection import project_strategy
from odin_backend.core.world_simulation.temporal_reasoning import analyze_timeline
from odin_backend.core.world_simulation.uncertainty_engine import quantify_uncertainty
from odin_backend.core.world_simulation.world_state import WorldStateStore


class WorldSimulationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._store = WorldStateStore(app.settings)
        self._graph = CausalWorldGraph()
        self._simulator = SimulationEngine()
        self._predictions = PredictionEngine()

    async def connect(self) -> None:
        await self._store.connect()

    async def disconnect(self) -> None:
        await self._store.disconnect()

    async def upsert_entity(self, *, name: str, kind: str, data: dict | None = None, confidence: float = 0.5) -> dict:
        result = await self._store.upsert_entity(name=name, kind=kind, data=data or {}, confidence=confidence)
        self._emit("world_state_changed", result)
        return result

    async def project(self, *, scenario: str, assumptions: list[str] | None = None, branches: int = 2) -> dict[str, Any]:
        if not getattr(self._app.settings, "world_simulation_enabled", False):
            return {"accepted": False, "reason": "world_simulation_disabled"}
        run = self._simulator.run(scenario=scenario, assumptions=assumptions or [], branches=branches)
        self._emit("simulation_projected", {"scenario": scenario, "run_id": run["id"]})
        return {"accepted": True, "simulation": run}

    async def predict(self, *, entity: str, hypothesis: str, mission_id: str | None = None, confidence: float = 0.6) -> dict:
        pred = self._predictions.predict(mission_id=mission_id, entity=entity, hypothesis=hypothesis, confidence=confidence)
        unc = quantify_uncertainty(confidence=pred["confidence"], evidence_count=1)
        pred["uncertainty"] = unc
        self._emit("prediction_updated", pred)
        return pred

    async def snapshot(self) -> dict[str, Any]:
        entities = await self._store.list_entities()
        relationships = await self._store.list_relationships()
        return {
            "entities": entities,
            "relationships": relationships,
            "causal_graph": self._graph.snapshot(),
            "simulations": self._simulator.list_runs()[-5:],
            "predictions": self._predictions.list_all()[-10:],
        }

    async def analyze_strategy(self, *, goal: str) -> dict[str, Any]:
        entities = await self._store.list_entities()
        projection = project_strategy(entities, goal=goal)
        scenarios = plan_scenarios(goal)
        timeline = analyze_timeline([{"confidence": e.get("confidence", 0.5)} for e in entities])
        return {"projection": projection, "scenarios": scenarios, "timeline": timeline}

    def add_causal_link(self, *, cause: str, effect: str, strength: float) -> dict:
        return self._graph.add_causal_link(cause=cause, effect=effect, strength=strength)

    def list_simulations(self) -> list[dict[str, Any]]:
        return self._simulator.list_runs()

    def predictions_for_mission(self, mission_id: str) -> list[dict[str, Any]]:
        return self._predictions.list_for_mission(mission_id)

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="world_simulation")

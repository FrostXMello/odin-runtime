"""Semantic planning pipeline — intent, strategy, decomposition, contracts."""

from __future__ import annotations

from typing import Any

from odin_backend.core.planning.confidence import (
    PlannerConfidenceProfile,
    compute_plan_confidence,
    confidence_action,
)
from odin_backend.core.planning.contracts import DynamicExecutionContract
from odin_backend.core.planning.decomposition import (
    CapabilityRequirement,
    decompose_objective,
    infer_capability,
    infer_tool,
    steps_to_contracts,
)
from odin_backend.core.planning.execution_strategy import ExecutionStrategy, select_strategy
from odin_backend.core.planning.horizon import HorizonPlan, LongHorizonPlanner, PlanningWave
from odin_backend.core.planning.objectives import ParsedObjective, parse_objective
from odin_backend.core.planning.reasoning import ReasoningGraph, ReasoningKind
from odin_backend.models.mission import Mission
from odin_backend.models.task_graph import TaskGraph, TaskNode, TaskNodeStatus
from pydantic import BaseModel, Field


class SemanticMissionPlan(BaseModel):
    objective: str
    parsed: dict[str, Any] = Field(default_factory=dict)
    strategy: dict[str, Any] = Field(default_factory=dict)
    task_graph: TaskGraph
    waves: list[PlanningWave] = Field(default_factory=list)
    milestones: list[str] = Field(default_factory=list)
    reasoning: dict[str, Any] = Field(default_factory=dict)
    confidence: dict[str, float] = Field(default_factory=dict)
    confidence_actions: dict[str, Any] = Field(default_factory=dict)
    contracts: dict[str, dict[str, Any]] = Field(default_factory=dict)
    capability_requirements: list[dict[str, Any]] = Field(default_factory=list)

    def to_horizon_plan(self) -> HorizonPlan:
        return HorizonPlan(
            objective=self.objective,
            task_graph=self.task_graph,
            waves=self.waves,
            milestones=self.milestones,
        )


class SemanticPlanner:
    """Semantic planning core — wraps horizon planner for DAG/wave construction."""

    def __init__(self, app: Any | None = None) -> None:
        self._app = app
        self._horizon = LongHorizonPlanner()
        self._last_plans: dict[str, SemanticMissionPlan] = {}

    def get_plan(self, mission_id: str) -> SemanticMissionPlan | None:
        return self._last_plans.get(mission_id)

    def plan(
        self,
        mission: Mission,
        *,
        context_summary: str = "",
        memory_hits: int = 0,
        prior_failures: int = 0,
    ) -> SemanticMissionPlan:
        parsed = parse_objective(mission.objective)
        if context_summary:
            parsed.constraints.append("context_enriched")

        sandbox = mission.execution_strategy == "sandbox_only"
        learning_profile = None
        memory_hints: list[dict[str, Any]] = []
        if self._app and getattr(self._app, "experience_engine", None):
            from odin_backend.core.planning.planner_feedback import build_learning_profile
            from odin_backend.core.planning.strategy_optimizer import optimize_strategy

            learning_profile = build_learning_profile(self._app)
            retrieval = getattr(self._app, "memory_retrieval", None)
            if retrieval:
                import asyncio

                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        pass
                    else:
                        memory_hints = loop.run_until_complete(
                            retrieval.nearest_successful(mission.objective)
                        )
                except RuntimeError:
                    pass
            strategy = optimize_strategy(
                parsed,
                learning_profile,
                sandbox_only=sandbox,
                autonomy_level=mission.autonomy_level,
            )
        else:
            strategy = select_strategy(
                parsed,
                sandbox_only=sandbox,
                autonomy_level=mission.autonomy_level,
            )

        reasoning = ReasoningGraph()
        root = reasoning.add(
            ReasoningKind.STRATEGY,
            f"Selected {strategy.kind.value}: {strategy.rationale}",
            confidence=0.8,
            evidence=strategy.model_dump(),
        )
        reasoning.add(
            ReasoningKind.ASSUMPTION,
            f"Intent inferred as {parsed.intent}",
            parent_id=root.node_id,
            assumptions=[f"domain={parsed.domain}"],
            confidence=0.75,
        )

        if learning_profile:
            from odin_backend.core.planning.adaptive_decomposition import decompose_with_learning

            steps = decompose_with_learning(
                parsed,
                strategy,
                learning_profile,
                mission_id=mission.mission_id,
                memory_hints=memory_hints,
            )
        else:
            steps = decompose_objective(parsed, strategy, mission_id=mission.mission_id)
        step_contracts = steps_to_contracts(steps)

        graph = TaskGraph()
        prev_id: str | None = None
        cap_reqs: list[CapabilityRequirement] = []
        contracts_out: dict[str, dict[str, Any]] = {}

        for i, step in enumerate(steps):
            req = infer_capability(parsed, step.goal)
            cap_reqs.append(req)
            contract = step_contracts[i]
            contract.confidence = step.confidence

            deps = [] if step.parallelizable and strategy.parallelizable else ([prev_id] if prev_id else [])
            if strategy.validation_first and i > 0 and not deps:
                deps = [prev_id] if prev_id else []

            node = TaskNode(
                goal=step.goal,
                dependencies=[d for d in deps if d],
                priority=max(10, 90 - i * 8),
                output=contract.to_task_output(),
            )
            node.output["step_kind"] = step.step_kind
            node.output["wave"] = 0
            graph.add_node(node)
            contracts_out[node.id] = contract.model_dump()
            prev_id = node.id

            reasoning.add(
                ReasoningKind.TOOL_DECISION,
                f"Task {node.id[:8]}: {step.capability} tool={step.tool}",
                task_id=node.id,
                parent_id=root.node_id,
                confidence=step.confidence,
                evidence={"capability": step.capability, "tool": step.tool},
            )
            if deps:
                reasoning.add(
                    ReasoningKind.DEPENDENCY,
                    f"Depends on {deps}",
                    task_id=node.id,
                    parent_id=root.node_id,
                    confidence=0.85,
                )

        _insert_validation_nodes(graph, contracts_out, reasoning, root.node_id)
        waves = self._horizon._build_waves(graph)
        milestones = [f"M{i + 1}: {w.task_ids[0][:8]}" for i, w in enumerate(waves) if w.task_ids]

        profile = compute_plan_confidence(
            step_count=len(graph.nodes),
            has_validation=any(n.output.get("type") == "validation" for n in graph.nodes.values()),
            memory_hits=memory_hits + len(memory_hints),
            prior_failures=prior_failures,
            tool_ambiguity=0.1 if len(set(r.capability for r in cap_reqs)) > 3 else 0.0,
        )
        if learning_profile:
            from odin_backend.core.planning.planner_feedback import apply_feedback_to_confidence

            profile_dict = apply_feedback_to_confidence(
                profile.to_dict(),
                learning_profile,
                strategy_kind=strategy.kind.value,
            )
            profile = PlannerConfidenceProfile(**profile_dict)
            if self._app:
                obs = getattr(self._app, "observability", None)
                if obs:
                    from odin_backend.core.observability.context import CausalTraceContext
                    from odin_backend.core.observability.events import TraceEventKind

                    obs.tracer.record(
                        TraceEventKind.PLANNER_IMPROVED,
                        message="learning-adjusted plan confidence",
                        payload={"strategy": strategy.kind.value, "confidence": profile_dict},
                        component="semantic_planner",
                        ctx=CausalTraceContext(mission_id=mission.mission_id),
                    )
        reasoning.add(
            ReasoningKind.CONFIDENCE,
            f"Plan confidence {profile.aggregate:.2f}",
            confidence=profile.aggregate,
            evidence=profile.to_dict(),
        )

        semantic = SemanticMissionPlan(
            objective=mission.objective,
            parsed=parsed.to_dict(),
            strategy=strategy.model_dump(),
            task_graph=graph,
            waves=waves,
            milestones=milestones,
            reasoning=reasoning.snapshot(),
            confidence=profile.to_dict(),
            confidence_actions=confidence_action(profile),
            contracts=contracts_out,
            capability_requirements=[
                {"capability": r.capability, "reason": r.reason, "confidence": r.confidence}
                for r in cap_reqs
            ],
        )
        self._last_plans[mission.mission_id] = semantic
        self._emit_traces(mission, semantic, reasoning)
        return semantic

    def replan(
        self,
        mission: Mission,
        *,
        reason: str = "reevaluation",
        memory_hits: int = 0,
    ) -> SemanticMissionPlan:
        reasoning = ReasoningGraph()
        root = reasoning.add(ReasoningKind.REPLAN, reason, confidence=0.7)

        pending = [
            n
            for n in mission.task_graph.nodes.values()
            if n.status in (TaskNodeStatus.PENDING, TaskNodeStatus.FAILED)
        ]
        if not pending:
            plan = self.plan(mission, memory_hits=memory_hits)
            plan.reasoning["nodes"].insert(
                0,
                root.to_trace_payload(),
            )
            return plan

        horizon = self._horizon.replan(mission, reason=reason)
        profile = compute_plan_confidence(
            step_count=len(horizon.task_graph.nodes),
            has_validation=True,
            memory_hits=memory_hits,
            prior_failures=sum(1 for n in mission.task_graph.nodes.values() if n.status == TaskNodeStatus.FAILED),
        )

        contracts: dict[str, dict[str, Any]] = {}
        for nid, node in horizon.task_graph.nodes.items():
            if node.output.get("type") == "execution" or node.output.get("capability"):
                c = DynamicExecutionContract.from_task_output(node.output)
                c.confidence = profile.task
                node.output = c.to_task_output()
                contracts[nid] = c.model_dump()

        semantic = SemanticMissionPlan(
            objective=mission.objective,
            parsed=parse_objective(mission.objective).to_dict(),
            strategy={"kind": "recovery", "rationale": reason},
            task_graph=horizon.task_graph,
            waves=horizon.waves,
            milestones=horizon.milestones,
            reasoning=reasoning.snapshot(),
            confidence=profile.to_dict(),
            confidence_actions=confidence_action(profile),
            contracts=contracts,
        )
        self._last_plans[mission.mission_id] = semantic
        self._emit_traces(mission, semantic, reasoning, replan=True)
        return semantic

    def expand_graph(
        self,
        mission: Mission,
        *,
        follow_up_goal: str,
        after_task_id: str | None = None,
        capability: str | None = None,
    ) -> TaskNode | None:
        """Insert planner-generated follow-up task without breaking DAG semantics."""
        parsed = parse_objective(follow_up_goal)
        req = infer_capability(parsed, follow_up_goal)
        cap = capability or req.capability
        contract = DynamicExecutionContract(
            capability=cap,
            tool=infer_tool(cap),
            params={"code": f"print({repr(follow_up_goal[:100])})"},
            confidence=req.confidence,
            metadata={"planner_expansion": True, "reason": "follow_up"},
        )
        deps = [after_task_id] if after_task_id else []
        node = TaskNode(
            goal=follow_up_goal,
            dependencies=[d for d in deps if d and d in mission.task_graph.nodes],
            priority=60,
            output=contract.to_task_output(),
        )
        mission.task_graph.add_node(node)
        mission.append_reasoning(
            "graph_expanded",
            detail={"task_id": node.id, "goal": follow_up_goal, "capability": cap},
        )
        plan = self._last_plans.get(mission.mission_id)
        if plan:
            plan.contracts[node.id] = contract.model_dump()
            plan.task_graph = mission.task_graph
        self._emit_trace(
            mission,
            "planner_reasoning",
            f"expanded graph: {follow_up_goal[:80]}",
            {"task_id": node.id},
        )
        return node

    def _emit_traces(
        self,
        mission: Mission,
        plan: SemanticMissionPlan,
        reasoning: ReasoningGraph,
        *,
        replan: bool = False,
    ) -> None:
        if not self._app:
            return
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.context import CausalTraceContext
        from odin_backend.core.observability.events import TraceEventKind

        ctx = CausalTraceContext(mission_id=mission.mission_id)
        kinds = [
            (TraceEventKind.STRATEGY_SELECTED, f"strategy {plan.strategy.get('kind')}"),
            (TraceEventKind.PLANNER_REASONING, "semantic plan generated"),
            (TraceEventKind.CONTRACT_GENERATED, f"{len(plan.contracts)} contracts"),
            (TraceEventKind.CONFIDENCE_UPDATED, f"aggregate {plan.confidence.get('plan', 0):.2f}"),
        ]
        if replan:
            kinds.append((TraceEventKind.REPLAN_GENERATED, "semantic replan"))
        for kind, msg in kinds:
            obs.tracer.record(
                kind,
                message=msg,
                payload={
                    "mission_id": mission.mission_id,
                    "reasoning": plan.reasoning,
                    "confidence": plan.confidence,
                },
                component="semantic_planner",
                ctx=ctx,
            )
        for node in reasoning.nodes[:20]:
            if node.kind == ReasoningKind.TOOL_DECISION:
                obs.tracer.record(
                    TraceEventKind.CAPABILITY_INFERRED,
                    message=node.message,
                    payload=node.to_trace_payload(),
                    component="semantic_planner",
                    ctx=ctx,
                )

    def _emit_trace(self, mission: Mission, kind_name: str, message: str, payload: dict) -> None:
        if not self._app:
            return
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.context import CausalTraceContext
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            kind = TraceEventKind.PLANNER_REASONING
        obs.tracer.record(
            kind,
            message=message,
            payload=payload,
            component="semantic_planner",
            ctx=CausalTraceContext(mission_id=mission.mission_id),
        )


def _insert_validation_nodes(
    graph: TaskGraph,
    contracts: dict[str, dict[str, Any]],
    reasoning: ReasoningGraph,
    parent_id: str,
) -> None:
    exec_nodes = [
        n for n in graph.nodes.values() if n.output.get("type") == "execution" and n.output.get("expected_output")
    ]
    for node in exec_nodes:
        expected = node.output.get("expected_output")
        if not expected:
            continue
        val = TaskNode(
            goal=f"Validate output: {expected}",
            dependencies=[node.id],
            priority=node.priority - 1,
            output={
                "type": "validation",
                "capability": "python.safe",
                "params": {"target": expected},
                "blocking": True,
                "validation": [{"kind": "exists", "target": expected}],
            },
        )
        graph.add_node(val)
        contracts[val.id] = DynamicExecutionContract(
            type="validation",
            capability="python.safe",
            params={"target": expected},
            validation=[],
            blocking=True,
        ).model_dump()
        reasoning.add(
            ReasoningKind.VALIDATION,
            f"Checkpoint for {node.id[:8]}",
            task_id=val.id,
            parent_id=parent_id,
            confidence=0.88,
        )

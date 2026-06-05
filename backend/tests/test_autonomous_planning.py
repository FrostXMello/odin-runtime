"""Autonomous planning and tool intelligence tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.execution.models import ExecutionState
from odin_backend.core.planning.confidence import (
    PlannerConfidenceProfile,
    compute_plan_confidence,
    confidence_action,
)
from odin_backend.core.planning.consistency import check_plan_consistency
from odin_backend.core.planning.contracts import (
    DynamicExecutionContract,
    ValidationRule,
    contract_for_step,
)
from odin_backend.core.planning.decomposition import (
    decompose_objective,
    infer_capability,
    infer_tool,
)
from odin_backend.core.planning.execution_strategy import StrategyKind, select_strategy
from odin_backend.core.planning.execution_verifier import verify_execution_result
from odin_backend.core.planning.objectives import parse_objective
from odin_backend.core.planning.output_validation import validate_contract_output
from odin_backend.core.planning.reasoning import ReasoningGraph, ReasoningKind
from odin_backend.core.planning.semantic_planner import SemanticPlanner
from odin_backend.core.planning.validators import PlanValidator
from odin_backend.core.runtime.adaptive_runtime import AdaptiveRuntimeCoordinator, _mission_plan_confidence
from odin_backend.core.tools.registry import IntelligentToolRegistry, ToolSpec
from odin_backend.core.tools.selector import ToolSelector
from odin_backend.core.tools.validation import validate_tool_input, validate_tool_output
from odin_backend.core.memory.context.embeddings import similarity
from odin_backend.core.memory.context.retrieval import PlannerRetriever
from odin_backend.core.memory.context.semantic_memory import SemanticMemoryEntry
from odin_backend.models.mission import Mission, MissionLifecycle
from odin_backend.models.task_graph import TaskGraph, TaskNode, TaskNodeStatus


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "plan.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        mission_gc_enabled=False,
        mission_restore_on_startup=False,
        execution_engine_enabled=True,
        queue_persist_enabled=True,
        async_mission_runtime_enabled=True,
        streaming_enabled=False,
    )


@pytest.fixture
async def app(settings, tmp_path):
    settings.chroma_persist_dir = tmp_path / "chroma"
    settings.sandbox_work_dir = tmp_path / "sandbox"
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


# --- Objectives ---


def test_parse_objective_research():
    p = parse_objective("Search the web for Odin runtime docs")
    assert p.domain == "research"
    assert "search" in p.verbs or p.intent == "research"


def test_parse_objective_multi_step():
    p = parse_objective("Analyze logs then deploy fix")
    assert p.intent == "multi_step"


def test_parse_objective_filesystem():
    p = parse_objective("Read file config.yaml and summarize")
    assert p.domain in ("filesystem", "general")


def test_parse_objective_safe_constraint():
    p = parse_objective("Run script safely")
    assert "safe_execution" in p.constraints


# --- Strategy ---


def test_select_strategy_research():
    p = parse_objective("research competitor APIs")
    s = select_strategy(p)
    assert s.kind == StrategyKind.RESEARCH_FIRST


def test_select_strategy_validation():
    p = parse_objective("generate report and validate schema")
    s = select_strategy(p)
    assert s.validation_first or s.kind == StrategyKind.VALIDATE_THEN_EXECUTE


def test_select_strategy_sandbox():
    p = parse_objective("run task")
    s = select_strategy(p, sandbox_only=True)
    assert s.kind == StrategyKind.SANDBOX_ONLY


def test_select_strategy_parallel():
    p = parse_objective("step one then step two")
    p.constraints.append("parallelizable")
    s = select_strategy(p)
    assert s.parallelizable or s.kind == StrategyKind.PARALLEL_WAVES


# --- Decomposition ---


def test_infer_capability_web():
    req = infer_capability(parse_objective("x"), "search for pricing data")
    assert req.capability == "web.search"


def test_infer_capability_python():
    req = infer_capability(parse_objective("x"), "execute python analysis")
    assert req.capability == "python.safe"


def test_infer_tool_mapping():
    assert infer_tool("filesystem.read") == "read_file"


def test_decompose_produces_steps():
    parsed = parse_objective("Analyze data then write report")
    strategy = select_strategy(parsed)
    steps = decompose_objective(parsed, strategy)
    assert len(steps) >= 2


def test_decompose_validation_first_inserts_preflight():
    parsed = parse_objective("validate output")
    parsed.constraints.append("requires_validation")
    strategy = select_strategy(parsed)
    steps = decompose_objective(parsed, strategy)
    assert any(s.step_kind == "validation" for s in steps) or strategy.validation_first


# --- Contracts ---


def test_dynamic_contract_to_task_output():
    c = contract_for_step(
        goal="run",
        capability="python.safe",
        tool=None,
        params={"code": "1"},
        confidence=0.9,
    )
    out = c.to_task_output()
    assert out["capability"] == "python.safe"
    assert out["confidence"] == 0.9


def test_contract_roundtrip():
    c = DynamicExecutionContract(capability="shell.safe", params={"cmd": "ls"})
    out = c.to_task_output()
    c2 = DynamicExecutionContract.from_task_output(out)
    assert c2.capability == "shell.safe"


def test_contract_validation_rules():
    c = DynamicExecutionContract(
        expected_output="report.json",
        validation=[ValidationRule(kind="exists", target="report.json")],
    )
    ok, issues = validate_contract_output(c, {"path": "report.json"})
    assert ok or len(issues) == 0


# --- Confidence ---


def test_confidence_profile_aggregate():
    p = PlannerConfidenceProfile(plan=0.8, task=0.7, tool=0.6, dependency=0.9, recovery=0.5)
    assert 0.5 < p.aggregate < 0.9


def test_compute_plan_confidence_memory_boost():
    p = compute_plan_confidence(step_count=3, has_validation=True, memory_hits=3)
    assert p.plan >= 0.75


def test_compute_plan_confidence_failure_penalty():
    p = compute_plan_confidence(step_count=3, has_validation=False, prior_failures=5)
    assert p.plan < 0.75


def test_confidence_action_low():
    actions = confidence_action(PlannerConfidenceProfile(plan=0.2, task=0.2, tool=0.2, dependency=0.2, recovery=0.2))
    assert actions["batch_size"] == 1


# --- Reasoning ---


def test_reasoning_graph_snapshot():
    g = ReasoningGraph()
    n = g.add(ReasoningKind.ASSUMPTION, "test assumption", confidence=0.8)
    g.add(ReasoningKind.INFERENCE, "child", parent_id=n.node_id)
    snap = g.snapshot()
    assert snap["node_count"] == 2
    assert len(snap["edges"]) == 1


# --- Semantic planner ---


def test_semantic_planner_plan():
    planner = SemanticPlanner()
    mission = Mission(objective="Analyze metrics then generate summary report")
    plan = planner.plan(mission)
    assert len(plan.task_graph.nodes) >= 2
    assert plan.confidence.get("plan", 0) > 0


def test_semantic_planner_reasoning_nodes():
    planner = SemanticPlanner()
    mission = Mission(objective="Search web then execute python script")
    plan = planner.plan(mission)
    assert plan.reasoning.get("node_count", 0) >= 2


def test_semantic_planner_contracts():
    planner = SemanticPlanner()
    mission = Mission(objective="Run analysis")
    plan = planner.plan(mission)
    assert len(plan.contracts) == len(plan.task_graph.nodes)


def test_semantic_planner_replan():
    planner = SemanticPlanner()
    mission = Mission(objective="Task A then Task B")
    initial = planner.plan(mission)
    mission.task_graph = initial.task_graph
    first_id = list(mission.task_graph.nodes.keys())[0]
    mission.task_graph.update_status(first_id, TaskNodeStatus.FAILED, strict=False)
    plan2 = planner.replan(mission, reason="test")
    assert plan2.task_graph.nodes


def test_semantic_planner_expand_graph():
    planner = SemanticPlanner()
    mission = Mission(objective="Initial task")
    planner.plan(mission)
    before = len(mission.task_graph.nodes)
    node = planner.expand_graph(mission, follow_up_goal="Follow up validation")
    assert node is not None
    assert len(mission.task_graph.nodes) > before


def test_semantic_to_horizon():
    planner = SemanticPlanner()
    mission = Mission(objective="Step one. Step two.")
    semantic = planner.plan(mission)
    horizon = semantic.to_horizon_plan()
    assert horizon.task_graph.nodes


# --- Consistency ---


def test_plan_consistency_ok():
    g = TaskGraph()
    a = TaskNode(goal="a")
    b = TaskNode(goal="b", dependencies=[a.id])
    g.add_node(a)
    g.add_node(b)
    r = check_plan_consistency(g)
    assert r["ok"]


def test_plan_consistency_cycle():
    g = TaskGraph()
    a = TaskNode(id="a", goal="a", dependencies=["b"])
    b = TaskNode(id="b", goal="b", dependencies=["a"])
    g.add_node(a)
    g.add_node(b)
    r = check_plan_consistency(g)
    assert not r["ok"]


# --- Tools ---


def test_intelligent_registry_builtin():
    reg = IntelligentToolRegistry()
    assert reg.get("read_file") is not None
    assert "filesystem.read" in reg.advertise_capabilities()


def test_tool_selector_python():
    reg = IntelligentToolRegistry()
    sel = ToolSelector(reg)
    choice = sel.select("python.safe")
    assert choice.capability == "python.safe"


def test_tool_selector_web():
    reg = IntelligentToolRegistry()
    sel = ToolSelector(reg)
    choice = sel.select("web.search")
    assert choice.tool == "search_web"


def test_tool_selector_memory_bias():
    reg = IntelligentToolRegistry()
    sel = ToolSelector(reg)
    c1 = sel.select("web.search", memory_bias={"search_web": 0.9})
    assert c1.confidence >= 0.7


def test_validate_tool_input():
    ok, errs = validate_tool_input(
        {"required": ["path"], "properties": {"path": {"type": "string"}}},
        {"path": "/tmp/x"},
    )
    assert ok


def test_validate_tool_output_fail():
    ok, msg = validate_tool_output({"error": "fail"})
    assert not ok


# --- Memory ---


def test_embedding_similarity():
    assert similarity("hello world", "hello odin world") > 0.2


def test_planner_retriever():
    r = PlannerRetriever()
    r.index(SemanticMemoryEntry(mission_id="m1", text="python data analysis pipeline", kind="strategy"))
    hits = r.retrieve("python analysis", mission_id="m1")
    assert hits


# --- Validators ---


def test_plan_validator():
    planner = SemanticPlanner()
    mission = Mission(objective="Do work")
    plan = planner.plan(mission)
    v = PlanValidator()
    result = v.validate_plan(plan.task_graph, plan.contracts)
    assert "consistent" in result


def test_execution_verifier():
    c = DynamicExecutionContract(blocking=True)
    r = verify_execution_result(c, {"success": False, "error": "x"})
    assert not r["ok"]


# --- Adaptive runtime ---


def test_mission_plan_confidence_dict():
    m = Mission(objective="x", confidence={"plan": 0.4, "task": 0.5, "tool": 0.5, "dependency": 0.5, "recovery": 0.5})
    assert _mission_plan_confidence(m) < 0.55


def test_adaptive_low_confidence_escalate():
    coord = AdaptiveRuntimeCoordinator()
    mission = Mission(objective="x", confidence={"plan": 0.2, "task": 0.2, "tool": 0.2, "dependency": 0.2, "recovery": 0.2})
    mission.metadata["semantic_plan"] = {"confidence_actions": {"validation_checkpoints": 3}}
    task = TaskNode(goal="t", output={"blocking": True})
    mission.task_graph.add_node(task)
    for _ in range(3):
        coord.record_outcome(mission.mission_id, task_id=task.id, success=False, execution_state="failed")
    d = coord.decide(None, mission, task, execution_state=ExecutionState.FAILED.value, contract_blocking=True)
    assert d.action in ("escalate", "replan", "retry", "isolate_branch")


# --- App integration ---


@pytest.mark.asyncio
async def test_app_semantic_plan_on_create(app):
    result = await app.mission_manager.create_checked(
        "Research Odin architecture then summarize findings",
        human_approved=True,
    )
    m = result.mission
    assert m.metadata.get("semantic_plan")
    assert len(m.task_graph.nodes) >= 2


@pytest.mark.asyncio
async def test_app_planner_api(app):
    await app.mission_manager.create_checked("Plan test mission", human_approved=True)
    snap = app.mission_execution_adaptive.snapshot(app)
    assert "missions" in snap


@pytest.mark.asyncio
async def test_app_tool_registry(app):
    health = await app.intelligent_tool_registry.health()
    assert health["tool_count"] >= 1


@pytest.mark.asyncio
async def test_app_tool_selector(app):
    sel = app.tool_selector.select("filesystem.read")
    assert sel.tool == "read_file"


@pytest.mark.asyncio
async def test_app_mission_context(app):
    result = await app.mission_manager.create_checked("Context test", human_approved=True)
    ctx = await app.mission_context.build_context(result.mission)
    assert "summary" in ctx


@pytest.mark.asyncio
async def test_app_mission_reasoning_endpoint_shape(app):
    result = await app.mission_manager.create_checked("Reasoning endpoint test", human_approved=True)
    plan = app.mission_planner.get_semantic_plan(result.mission.mission_id)
    assert plan is not None
    assert plan.reasoning


@pytest.mark.asyncio
async def test_mission_planner_expand(app):
    result = await app.mission_manager.create_checked("Expand graph test", human_approved=True)
    m = result.mission
    n = app.mission_planner.expand(m, follow_up_goal="Verify outputs")
    assert n is not None


@pytest.mark.asyncio
async def test_trace_kinds_exist():
    from odin_backend.core.observability.events import TraceEventKind

    assert TraceEventKind.PLANNER_REASONING.value == "planner_reasoning"
    assert TraceEventKind.STRATEGY_SELECTED.value == "strategy_selected"


def test_long_horizon_iterative_strategy():
    p = parse_objective("analyze build deploy monitor")
    s = select_strategy(p, autonomy_level=5)
    assert s.kind == StrategyKind.ITERATIVE


def test_capability_requirements_in_plan():
    planner = SemanticPlanner()
    mission = Mission(objective="Search then write file output.txt")
    plan = planner.plan(mission)
    assert len(plan.capability_requirements) >= 1


@pytest.mark.asyncio
async def test_stream_channels_planner():
    from odin_backend.core.observability.events import TraceEvent, TraceEventKind
    from odin_backend.core.streaming.serializers import resolve_channels_for_trace

    ev = TraceEvent(
        kind=TraceEventKind.PLANNER_REASONING,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
        mission_id="mid",
    )
    ch = resolve_channels_for_trace(ev)
    assert "planner:runtime" in ch
    assert "reasoning:mission:mid" in ch

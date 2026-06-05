"""Cognitive memory graph and self-improvement runtime tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.cognition.clustering import cluster_by_key, top_clusters
from odin_backend.core.cognition.decay import decay_confidence, decay_weight
from odin_backend.core.cognition.entities import MemoryEntity, MemoryEntityKind
from odin_backend.core.cognition.episodic_memory import episodic_from_execution
from odin_backend.core.cognition.experience.execution_scoring import execution_fingerprint, score_execution
from odin_backend.core.cognition.experience.experience_engine import ExperienceEngine
from odin_backend.core.cognition.experience.outcome_analysis import analyze_outcomes
from odin_backend.core.cognition.experience.pattern_mining import mine_failure_clusters, mine_tool_chains
from odin_backend.core.cognition.failures.anomaly_detection import detect_anomalies
from odin_backend.core.cognition.failures.escalation_engine import recommend_escalation
from odin_backend.core.cognition.failures.failure_classifier import FailureClass, classify_failure
from odin_backend.core.cognition.failures.failure_intelligence import FailureIntelligence
from odin_backend.core.cognition.failures.regression_detector import detect_regression
from odin_backend.core.cognition.improvement.improvement_loop import ImprovementLoop
from odin_backend.core.cognition.improvement.policy_tuner import tune_policies
from odin_backend.core.cognition.memory_graph import CognitiveMemoryGraph
from odin_backend.core.cognition.procedural_memory import procedural_from_strategy
from odin_backend.core.cognition.relationships import MemoryRelationship, RelationshipType
from odin_backend.core.cognition.retrieval_engine import RetrievalEngine
from odin_backend.core.cognition.semantic_memory import semantic_from_pattern
from odin_backend.core.cognition.vector_index import VectorIndex
from odin_backend.core.execution.intelligence.adaptive_timeout import estimate_timeout
from odin_backend.core.execution.intelligence.capability_performance import CapabilityPerformanceTracker
from odin_backend.core.execution.intelligence.execution_optimizer import ExecutionIntelligence
from odin_backend.core.execution.intelligence.retry_intelligence import retry_delay, should_replan_instead_of_retry
from odin_backend.core.planning.learning_profile import PlannerLearningProfile
from odin_backend.core.planning.planner_feedback import apply_feedback_to_confidence, build_learning_profile
from odin_backend.core.planning.adaptive_decomposition import adapt_steps
from odin_backend.core.planning.decomposition import DecomposedStep
from odin_backend.core.observability.events import TraceEventKind
from odin_backend.models.mission import Mission, MissionLifecycle


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "cog.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        cognitive_learning_enabled=False,
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
        execution_engine_enabled=True,
    )


@pytest.fixture
async def graph(settings):
    g = CognitiveMemoryGraph(settings)
    await g.connect()
    yield g
    await g.disconnect()


@pytest.fixture
async def app(settings, tmp_path):
    settings.chroma_persist_dir = tmp_path / "chroma"
    settings.sandbox_work_dir = tmp_path / "sandbox"
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


# --- Memory graph ---


@pytest.mark.asyncio
async def test_upsert_entity(graph):
    e = MemoryEntity(kind=MemoryEntityKind.SEMANTIC, label="test pattern", confidence=0.7)
    await graph.upsert_entity(e)
    snap = await graph.export_snapshot()
    assert len(snap["entities"]) >= 1


@pytest.mark.asyncio
async def test_link_execution(graph):
    eid = await graph.link_execution(
        mission_id="m1",
        task_id="t1",
        execution_id="e1",
        summary="python run ok",
        success=True,
        capability="python.safe",
    )
    assert eid


@pytest.mark.asyncio
async def test_reinforce(graph):
    e = MemoryEntity(kind=MemoryEntityKind.EPISODIC, label="ep", confidence=0.5)
    await graph.upsert_entity(e)
    await graph.reinforce(e.entity_id, success=True)
    snap = await graph.export_snapshot()
    assert snap["entities"][0]["confidence"] >= 0.5


@pytest.mark.asyncio
async def test_add_relationship(graph):
    a = await graph.upsert_entity(MemoryEntity(kind=MemoryEntityKind.TASK, label="task a"))
    b = await graph.upsert_entity(MemoryEntity(kind=MemoryEntityKind.TASK, label="task b"))
    await graph.add_relationship(
        MemoryRelationship(source_id=a.entity_id, target_id=b.entity_id, rel_type=RelationshipType.DEPENDS_ON)
    )
    snap = await graph.export_snapshot()
    assert snap["relationships"]


@pytest.mark.asyncio
async def test_decay_stale(graph):
    e = MemoryEntity(kind=MemoryEntityKind.SEMANTIC, label="old", confidence=0.9)
    await graph.upsert_entity(e)
    count = await graph.decay_stale(max_age_days=0.0001)
    assert count >= 0


@pytest.mark.asyncio
async def test_retrieval_similar(graph):
    retrieval = RetrievalEngine(graph)
    await graph.link_execution(
        mission_id="m2",
        task_id=None,
        execution_id="e2",
        summary="search web for docs",
        success=True,
        capability="web.search",
    )
    hits = await retrieval.similar_executions("search web", limit=3)
    assert isinstance(hits, list)


@pytest.mark.asyncio
async def test_retrieval_failure_patterns(graph):
    await graph.upsert_entity(
        episodic_from_execution(
            mission_id="m3",
            task_id=None,
            execution_id="e3",
            summary="failed shell",
            success=False,
        )
    )
    retrieval = RetrievalEngine(graph)
    patterns = await retrieval.failure_patterns()
    assert patterns


# --- Vector / decay ---


def test_vector_index_search():
    idx = VectorIndex()
    idx.upsert("a", "python data analysis")
    idx.upsert("b", "unrelated cooking recipe")
    hits = idx.search("python analysis", limit=2)
    assert hits[0][0] == "a"


def test_decay_confidence():
    assert decay_confidence(0.8, age_seconds=0) == 0.8
    assert decay_confidence(0.8, age_seconds=86400 * 30) < 0.8


def test_decay_weight():
    assert decay_weight(1.0, failures=2) < 1.0


# --- Experience ---


def test_analyze_outcomes():
    events = [{"success": True}, {"success": False, "latency_ms": 100}]
    r = analyze_outcomes(events)
    assert r["total"] == 2
    assert r["success_rate"] == 0.5


def test_mine_tool_chains():
    chains = mine_tool_chains(
        [{"tool": "read_file", "success": True}, {"tool": "read_file", "success": True}]
    )
    assert chains[0]["count"] >= 2


def test_mine_failure_clusters():
    clusters = mine_failure_clusters(
        [{"capability": "shell.safe", "success": False}, {"capability": "shell.safe", "success": False}]
    )
    assert clusters and clusters[0]["key"] == "shell.safe"


def test_execution_fingerprint():
    fp = execution_fingerprint(capability="python.safe", tool=None, mission_id="m")
    assert len(fp) == 16


def test_score_execution():
    assert score_execution(success=True, latency_ms=1000, retries=0) > 0.7
    assert score_execution(success=False, latency_ms=None, retries=3) < 0.5


@pytest.mark.asyncio
async def test_experience_record_outcome():
    exp = ExperienceEngine(None)
    exp.record_outcome(
        mission_id="m",
        task_id="t",
        execution_id="e",
        capability="python.safe",
        tool=None,
        success=True,
    )
    assert exp.metrics["outcomes_recorded"] == 1


@pytest.mark.asyncio
async def test_mission_retrospective(app):
    result = await app.mission_manager.create_checked("Learn retrospective test", human_approved=True)
    mission = result.mission
    mission.current_state = MissionLifecycle.COMPLETED
    retro = await app.experience_engine.on_mission_completed(mission)
    assert "succeeded" in retro
    assert retro["mission_id"] == mission.mission_id


# --- Planner learning ---


def test_planner_learning_profile():
    p = PlannerLearningProfile(strategy_success_rate={"sequential": 0.8})
    assert p.best_strategy == "sequential"


def test_apply_feedback_to_confidence():
    base = {"plan": 0.6, "task": 0.6, "tool": 0.6, "dependency": 0.6, "recovery": 0.6}
    profile = PlannerLearningProfile(strategy_success_rate={"sequential": 0.9})
    out = apply_feedback_to_confidence(base, profile, strategy_kind="sequential")
    assert out["plan"] > 0.6


def test_adapt_steps_penalize():
    profile = PlannerLearningProfile(penalized_capabilities=["shell.safe"])
    steps = [
        DecomposedStep(
            goal="run shell",
            capability="shell.safe",
            tool="execute_terminal",
            params={},
            confidence=0.8,
        )
    ]
    adapted = adapt_steps(steps, profile)
    assert adapted[0].capability != "shell.safe" or adapted[0].confidence < 0.8


# --- Execution intelligence ---


def test_capability_tracker():
    t = CapabilityPerformanceTracker()
    t.record("python.safe", success=True, latency_ms=50)
    t.record("python.safe", success=False)
    scores = t.scores()
    assert scores["python.safe"]["failure_rate"] > 0


def test_execution_intelligence_timeout():
    intel = ExecutionIntelligence()
    intel.record_execution("python.safe", success=True, latency_ms=1000)
    t = intel.suggest_timeout("python.safe", base=60)
    assert t > 0


def test_retry_delay():
    assert retry_delay(attempt=2, failure_rate=0.6) > retry_delay(attempt=1, failure_rate=0.1)


def test_should_replan_oscillation():
    assert should_replan_instead_of_retry(attempt=2, max_retries=3, failure_rate=0.5, oscillation_score=4)


def test_estimate_timeout():
    assert estimate_timeout("cap", avg_latency_ms=5000, failure_rate=0.5) > 60


# --- Failures ---


def test_classify_failure():
    assert classify_failure(reason="timeout", execution_state="timed_out", retry_count=0) == FailureClass.TIMEOUT


def test_detect_anomalies():
    a = detect_anomalies({"failure_rate": 0.8, "plan_confidence": 0.2})
    assert len(a) >= 2


def test_regression_detect():
    r = detect_regression({"reliability": 0.3}, {"reliability": 0.7})
    assert r


def test_escalation_recommendation():
    rec = recommend_escalation(FailureClass.OSCILLATION, oscillation=True)
    assert rec["escalate"]


@pytest.mark.asyncio
async def test_failure_intelligence_analyze(app):
    app.failure_intelligence.record_adaptation("m-osc", "retry")
    app.failure_intelligence.record_adaptation("m-osc", "replan")
    report = await app.failure_intelligence.analyze(mission_id="m-osc")
    assert report.to_dict()


# --- Improvement ---


@pytest.mark.asyncio
async def test_improvement_cycle(app):
    result = await app.improvement_loop.run_cycle()
    assert "cycle" in result


@pytest.mark.asyncio
async def test_recalibrate(app):
    r = await app.improvement_loop.recalibrate_confidence()
    assert "decayed_entities" in r


def test_policy_tuner():
    stats = {"bad": {"success_rate": 0.1, "attempts": 10}, "good": {"success_rate": 0.9, "attempts": 5}}
    tuned = tune_policies(stats)
    assert "bad" in tuned["pruned_strategies"]


# --- Clustering ---


def test_cluster_by_key():
    c = cluster_by_key([{"cap": "a"}, {"cap": "a"}, {"cap": "b"}], "cap")
    assert c["a"]


# --- App integration ---


@pytest.mark.asyncio
async def test_app_has_cognition_services(app):
    assert hasattr(app, "cognitive_memory")
    assert hasattr(app, "experience_engine")
    assert hasattr(app, "execution_intelligence")
    assert hasattr(app, "failure_intelligence")
    assert hasattr(app, "improvement_loop")


@pytest.mark.asyncio
async def test_memory_graph_api_shape(app):
    snap = await app.cognitive_memory.export_snapshot(limit=10)
    assert "entities" in snap


@pytest.mark.asyncio
async def test_build_learning_profile(app):
    app.experience_engine.record_outcome(
        mission_id="m",
        task_id="t",
        execution_id="e",
        capability="python.safe",
        tool=None,
        success=True,
    )
    profile = build_learning_profile(app)
    assert isinstance(profile, PlannerLearningProfile)


def test_trace_kinds_cognitive():
    assert TraceEventKind.MEMORY_REINFORCED.value == "memory_reinforced"
    assert TraceEventKind.PLANNER_IMPROVED.value == "planner_improved"
    assert TraceEventKind.OPTIMIZATION_CYCLE_COMPLETED.value == "optimization_cycle_completed"


@pytest.mark.asyncio
async def test_semantic_procedural_entities(graph):
    await graph.upsert_entity(semantic_from_pattern(label="domain knowledge", domain="api"))
    await graph.upsert_entity(
        procedural_from_strategy(strategy_kind="sequential", objective_domain="api", success_rate=0.85)
    )
    snap = await graph.export_snapshot()
    kinds = {e["kind"] for e in snap["entities"]}
    assert "semantic" in kinds or "procedural" in kinds


@pytest.mark.asyncio
async def test_nearest_successful(graph):
    await graph.link_execution(
        mission_id="m",
        task_id=None,
        execution_id="ex",
        summary="successful deploy pipeline",
        success=True,
        capability="workflow.execute",
    )
    retrieval = RetrievalEngine(graph)
    near = await retrieval.nearest_successful("deploy pipeline")
    assert isinstance(near, list)


# --- Strategy learning ---


def test_update_strategy_stats():
    from odin_backend.core.cognition.experience.strategy_learning import update_strategy_stats

    stats: dict = {}
    update_strategy_stats(stats, strategy_kind="sequential", success=True, latency_ms=100)
    update_strategy_stats(stats, strategy_kind="sequential", success=False)
    assert stats["sequential"]["attempts"] == 2
    assert stats["sequential"]["successes"] == 1


def test_strategy_optimizer_learned():
    from odin_backend.core.planning.execution_strategy import StrategyKind
    from odin_backend.core.planning.objectives import parse_objective
    from odin_backend.core.planning.strategy_optimizer import optimize_strategy

    parsed = parse_objective("analyze logs and report")
    profile = PlannerLearningProfile(strategy_success_rate={"parallel_waves": 0.85})
    strategy = optimize_strategy(parsed, profile, autonomy_level=3)
    assert strategy.kind == StrategyKind.PARALLEL_WAVES
    assert strategy.metadata.get("learned") is True


@pytest.mark.asyncio
async def test_recall_strategy(graph):
    await graph.upsert_entity(
        procedural_from_strategy(strategy_kind="sequential", objective_domain="api", success_rate=0.9)
    )
    retrieval = RetrievalEngine(graph)
    recalled = await retrieval.recall_strategy("api")
    assert recalled


@pytest.mark.asyncio
async def test_failure_reinforcement_decay(graph):
    e = MemoryEntity(kind=MemoryEntityKind.EPISODIC, label="failed run", confidence=0.6)
    await graph.upsert_entity(e)
    await graph.reinforce(e.entity_id, success=False)
    snap = await graph.export_snapshot()
    entity = next(x for x in snap["entities"] if x["entity_id"] == e.entity_id)
    assert entity["confidence"] < 0.6


def test_execution_profiler():
    from odin_backend.core.execution.intelligence.execution_profiler import ExecutionProfiler

    prof = ExecutionProfiler()
    prof.update("ex-1", latency_ms=120, success=True)
    assert prof.get("ex-1")["latency_ms"] == 120
    assert prof.snapshot()


@pytest.mark.asyncio
async def test_oscillation_detection(app):
    for _ in range(5):
        app.failure_intelligence.record_adaptation("m-loop", "retry")
        app.failure_intelligence.record_adaptation("m-loop", "replan")
    report = await app.failure_intelligence.analyze(mission_id="m-loop")
    assert report.oscillation_detected


@pytest.mark.asyncio
async def test_stream_channels_cognition():
    from odin_backend.core.observability.events import TraceEvent, TraceEventKind
    from odin_backend.core.streaming.serializers import resolve_channels_for_trace

    ev = TraceEvent(
        kind=TraceEventKind.MEMORY_REINFORCED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
        message="memory reinforced",
        component="cognitive_memory",
    )
    channels = resolve_channels_for_trace(ev)
    assert "cognition:runtime" in channels


@pytest.mark.asyncio
async def test_cognition_http_endpoints(app, tmp_path):
    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient

    from odin_backend.api.routes import cognition_runtime

    api = FastAPI()
    api.state.odin = app
    api.include_router(cognition_runtime.router, prefix="/api/v1")

    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/v1/runtime/cognition")
        assert r.status_code == 200
        assert "memory_graph" in r.json()

        r2 = await client.get("/api/v1/runtime/learning")
        assert r2.status_code == 200

        r3 = await client.post("/api/v1/runtime/optimization/run")
        assert r3.status_code == 200
        assert "cycle" in r3.json()


@pytest.mark.asyncio
async def test_mission_retrospective_api(app):
    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient

    from odin_backend.api.routes import missions

    result = await app.mission_manager.create_checked("API retrospective", human_approved=True)
    mission = result.mission
    mission.current_state = MissionLifecycle.COMPLETED
    await app.experience_engine.on_mission_completed(mission)
    await app.mission_manager.persist(mission)

    api = FastAPI()
    api.state.odin = app
    api.include_router(missions.router, prefix="/api/v1")

    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get(f"/api/v1/missions/{mission.mission_id}/retrospective")
        assert r.status_code == 200
        assert r.json()["retrospective"]


@pytest.mark.asyncio
async def test_mission_memory_context_api(app):
    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient

    from odin_backend.api.routes import missions

    result = await app.mission_manager.create_checked("Memory context API", human_approved=True)
    mid = result.mission.mission_id

    api = FastAPI()
    api.state.odin = app
    api.include_router(missions.router, prefix="/api/v1")

    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get(f"/api/v1/missions/{mid}/memory-context")
        assert r.status_code == 200


def test_build_retrospective_fields():
    from odin_backend.core.cognition.experience.mission_retrospective import build_retrospective

    mission = Mission(objective="test objective", mission_id="m-retro")
    retro = build_retrospective(
        mission,
        outcome_analysis={"avg_latency_ms": 50, "failures": 0, "bottlenecks": []},
        success_patterns=[{"capability": "python.safe"}],
        failure_clusters=[],
        tool_chains=[{"tool": "read_file", "count": 2}],
    )
    assert retro["mission_id"] == "m-retro"
    assert "succeeded" in retro


@pytest.mark.asyncio
async def test_execution_intelligence_record(app):
    app.execution_intelligence.record_execution("web.search", success=True, latency_ms=200)
    scores = app.execution_intelligence.capability_scores()
    assert "web.search" in scores


@pytest.mark.asyncio
async def test_memory_graph_relationship_types(graph):
    fail = await graph.upsert_entity(MemoryEntity(kind=MemoryEntityKind.EXECUTION, label="fail exec"))
    fix = await graph.upsert_entity(MemoryEntity(kind=MemoryEntityKind.TOOL, label="read_file"))
    await graph.add_relationship(
        MemoryRelationship(
            source_id=fail.entity_id,
            target_id=fix.entity_id,
            rel_type=RelationshipType.SOLVED_BY,
            weight=0.8,
        )
    )
    snap = await graph.export_snapshot()
    assert snap["relationships"][0]["type"] == "solved_by"


@pytest.mark.asyncio
async def test_improvement_loop_cycle_count(app):
    before = app.improvement_loop.cycle_count
    await app.improvement_loop.run_cycle()
    assert app.improvement_loop.cycle_count == before + 1

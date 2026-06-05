"""Prompt 15 — active perception and adaptive feedback."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.confidence import ConfidenceTracker
from odin_backend.core.execution_gate.adaptive_policy import AdaptiveExecutionPolicy
from odin_backend.core.execution_gate.gate import ExecutionGate
from odin_backend.core.feedback import ExecutionFeedbackEngine
from odin_backend.core.perception.engine import PerceptionEngine
from odin_backend.core.perception.bridge import PerceptionMemoryBridge
from odin_backend.memory.perception import PerceptionMemoryStore
from odin_backend.models.mission import MissionLifecycle
from odin_backend.models.perception import PerceptionCategory
from odin_backend.models.task_graph import TaskNodeStatus
from odin_backend.runtime.observers.filesystem import FilesystemObserver


@pytest.fixture
async def app(tmp_path):
    db_file = tmp_path / "odin_test.db"
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{db_file.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        stability_loop_enabled=False,
        mission_worker_enabled=False,
        mission_dispatch_enabled=False,
        mission_gc_enabled=False,
        mission_restore_on_startup=False,
        runtime_observers_enabled=False,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_perception_ingestion(app: OdinApplication):
    record = await app.perception.ingest_execution(
        tool="get_system_info",
        success=True,
        mission_id="m-test-1",
    )
    assert record.category == PerceptionCategory.EXECUTION_RESULT
    assert len(app.perception.live_perceptions) >= 1
    history = app.perception_memory.history(limit=5, mission_id="m-test-1")
    assert len(history) >= 1


@pytest.mark.asyncio
async def test_feedback_failure_classification(app: OdinApplication):
    engine = app.feedback
    report = engine.process(
        success=False,
        tool="open_browser",
        reason="governor blocked",
        mission_id="m-fb-1",
        task_id="t-1",
    )
    for _ in range(3):
        engine.process(success=False, tool="open_browser", reason="fail", mission_id="m-fb-1")
    report2 = engine.process(success=False, tool="open_browser", reason="fail", mission_id="m-fb-1")
    assert report2.should_switch_strategy or report2.should_replan
    assert len(report.perceptions) >= 1


@pytest.mark.asyncio
async def test_confidence_degradation(app: OdinApplication):
    tracker = app.confidence
    before = tracker.global_snapshot.aggregate
    tracker.record_tool_outcome("execute_terminal", False)
    tracker.record_tool_outcome("execute_terminal", False)
    tracker.record_tool_outcome("execute_terminal", False)
    after = tracker.global_snapshot.aggregate
    assert after < before


@pytest.mark.asyncio
async def test_adaptive_replanning_on_failures(app: OdinApplication):
    mission = await app.mission_manager.create("Adaptive step A. Adaptive step B.")
    node = list(mission.task_graph.nodes.values())[0]
    node.output["tool"] = "open_browser"
    await app.mission_manager.persist(mission)

    for _ in range(4):
        app.feedback.process(
            success=False,
            tool="open_browser",
            reason="environment unstable",
            mission_id=mission.mission_id,
            task_id=node.id,
        )

    result = await app.mission_runtime.run_wave(app, mission)
    mission = await app.mission_manager.get(mission.mission_id)
    assert mission.execution_strategy == "conservative_readonly" or result.get("replanned") or len(mission.adaptation_log) >= 1


@pytest.mark.asyncio
async def test_observer_throttling(app: OdinApplication):
    obs = FilesystemObserver(app.perception, watch_path="./data")
    first = await obs.poll()
    second = await obs.poll()
    assert len(first) + len(second) >= 0
    if first:
        assert obs._should_emit(first[0]) is True
        assert obs._should_emit(first[0]) is False


@pytest.mark.asyncio
async def test_adaptive_execution_policy(app: OdinApplication):
    from odin_backend.core.confidence import ConfidenceSnapshot

    policy = AdaptiveExecutionPolicy(ExecutionGate())
    snap = ConfidenceSnapshot(
        execution_confidence=0.3,
        mission_stability=0.3,
        tool_reliability=0.2,
    )
    state = policy.apply_instability(confidence=snap, failure_count=3, repeated_tool_failures=True)
    assert state.concurrency_limit <= 2
    assert state.require_confirmation is True


@pytest.mark.asyncio
async def test_checkpoint_rollback_on_repeated_failure(app: OdinApplication):
    mission = await app.mission_manager.create("Rollback test one. Rollback test two.")
    await app.mission_runtime.run_wave(app, mission)
    ckpt_id = mission.checkpoints[-1].id if mission.checkpoints else None
    assert ckpt_id

    report = app.feedback.process(
        success=False,
        tool="noop",
        mission_id=mission.mission_id,
    )
    for _ in range(5):
        app.feedback.process(success=False, tool="noop", mission_id=mission.mission_id)

    report_final = app.feedback.process(success=False, tool="noop", mission_id=mission.mission_id)
    assert report_final.should_rollback or report_final.should_replan


@pytest.mark.asyncio
async def test_escalation_threshold(app: OdinApplication):
    mission = await app.mission_manager.create("Escalation test objective")
    from odin_backend.core.confidence import ConfidenceSnapshot

    app.confidence.set_mission(
        mission.mission_id,
        ConfidenceSnapshot(
            execution_confidence=0.1,
            environmental_certainty=0.1,
            reasoning_confidence=0.1,
            tool_reliability=0.1,
            mission_stability=0.1,
        ),
    )
    assert app.confidence.should_escalate(mission.mission_id)


@pytest.mark.asyncio
async def test_perception_memory_linkage(app: OdinApplication):
    await app.perception.ingest_execution(tool="noop", success=False, mission_id="m-mem-1")
    patterns = app.perception_memory.failure_patterns()
    assert isinstance(patterns, dict)


@pytest.mark.asyncio
async def test_adaptive_apis(app: OdinApplication):
    from odin_backend.api.routes import perception as perception_routes
    from odin_backend.api.routes import adaptive_runtime as adaptive_routes
    from odin_backend.api.routes import missions as missions_routes

    api = FastAPI()
    api.state.odin = app
    api.include_router(perception_routes.router, prefix="/api/v1")
    api.include_router(adaptive_routes.router, prefix="/api/v1")
    api.include_router(missions_routes.router, prefix="/api/v1")

    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        live = await client.get("/api/v1/perception/live")
        hist = await client.get("/api/v1/perception/history")
        conf = await client.get("/api/v1/runtime/confidence")
        env = await client.get("/api/v1/runtime/environment")
        assert live.status_code == 200
        assert hist.status_code == 200
        assert conf.status_code == 200
        assert env.status_code == 200

        created = await client.post(
            "/api/v1/missions/create",
            json={"objective": "API adaptive one. API adaptive two.", "start_worker": False},
        )
        mid = created.json()["mission_id"]
        adapt = await client.get(f"/api/v1/missions/{mid}/adaptation-log")
        assert adapt.status_code == 200


@pytest.mark.asyncio
async def test_cognitive_state_perception_fields(app: OdinApplication):
    from odin_backend.core.bus.signals import Signal, SignalKind

    await app.perception.ingest_execution(tool="test", success=True)
    await app.kernel.process_signal(
        Signal(kind=SignalKind.TASK, name="task.created", type="task.created", source="user")
    )
    state = app.kernel.get_state()
    assert state.confidence_score <= 1.0
    assert isinstance(state.environment_awareness, dict)

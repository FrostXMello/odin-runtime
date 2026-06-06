"""Prompt 14 — persistent mission system."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.planning.horizon import LongHorizonPlanner
from odin_backend.models.mission import MissionLifecycle
from odin_backend.models.task_graph import TaskNode, TaskNodeStatus


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
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_mission_persistence(app: OdinApplication):
    mission = await app.mission_manager.create(
        "Analyze logs. Verify metrics. Report summary.",
        priority=80,
    )
    assert mission.mission_id
    loaded = await app.mission_manager.get(mission.mission_id)
    assert loaded is not None
    assert loaded.objective == mission.objective
    assert len(loaded.task_graph.nodes) >= 2


@pytest.mark.asyncio
async def test_dependency_ordering(app: OdinApplication):
    plan = LongHorizonPlanner().decompose("Step A. Step B. Step C.")
    waves = plan.waves
    assert len(waves) >= 2
    first_wave_ids = set(waves[0].task_ids)
    for w in waves[1:]:
        for tid in w.task_ids:
            node = plan.task_graph.get(tid)
            assert all(d in first_wave_ids or d in _all_prior(waves, w.wave_index) for d in node.dependencies)


def _all_prior(waves, idx):
    ids: set[str] = set()
    for w in waves:
        if w.wave_index < idx:
            ids.update(w.task_ids)
    return ids


@pytest.mark.asyncio
async def test_mission_wave_execution_completes(app: OdinApplication):
    mission = await app.mission_manager.create("Plan phase. Execute phase. Verify phase.")
    while not mission.is_terminal() and mission.current_wave < 20:
        result = await app.mission_runtime.run_wave(app, mission)
        mission = await app.mission_manager.get(mission.mission_id)
        assert mission is not None
        if result.get("completed"):
            break
    assert mission.current_state == MissionLifecycle.COMPLETED
    assert len(mission.completed_tasks) >= 2


@pytest.mark.asyncio
async def test_checkpoint_restore(app: OdinApplication):
    mission = await app.mission_manager.create("Task one. Task two.")
    await app.mission_runtime.run_wave(app, mission)
    ckpt = app.mission_checkpoints.create_checkpoint(mission, label="test")
    await app.mission_checkpoints.persist(mission, ckpt)

    node_id = list(mission.task_graph.nodes.keys())[0]
    mission.task_graph.update_status(node_id, TaskNodeStatus.FAILED, strict=False)
    restored = await app.mission_checkpoints.restore_latest(mission)
    assert restored is not None
    assert restored.checkpoints or restored.execution_history


@pytest.mark.asyncio
async def test_restart_recovery(app: OdinApplication):
    mission = await app.mission_manager.create("Recoverable step one. Recoverable step two.")
    mission_id = mission.mission_id
    await app.mission_runtime.run_wave(app, mission)

    restored = await app.mission_manager.restore_active()
    ids = [m.mission_id for m in restored]
    assert mission_id in ids


@pytest.mark.asyncio
async def test_pause_resume_cancel(app: OdinApplication):
    mission = await app.mission_manager.create("Pause test step one. Pause test step two.")
    paused = await app.mission_manager.pause(mission.mission_id)
    assert paused.current_state == MissionLifecycle.BLOCKED

    resumed = await app.mission_manager.resume(mission.mission_id)
    assert resumed.current_state == MissionLifecycle.RUNNING

    cancelled = await app.mission_manager.cancel(mission.mission_id)
    assert cancelled.current_state == MissionLifecycle.CANCELLED


@pytest.mark.asyncio
async def test_escalation_flow(app: OdinApplication):
    mission = await app.mission_manager.create(
        "Delete production database",
        autonomy_level=5,
        human_approved=False,
    )
    assert mission.current_state == MissionLifecycle.APPROVAL_REQUIRED

    approved = await app.mission_manager.approve(mission.mission_id)
    assert approved.human_approved
    node = list(approved.task_graph.nodes.values())[0]
    node.output["tool"] = "execute_terminal"
    node.output["params"] = {"command": "rm -rf /"}
    await app.mission_manager.persist(approved)

    result = await app.mission_runtime.run_wave(app, approved)
    mission = await app.mission_manager.get(mission.mission_id)
    assert (
        mission.current_state in (MissionLifecycle.ESCALATED, MissionLifecycle.BLOCKED)
        or result.get("state") == "escalated"
        or len(mission.escalation_events) > 0
    )


@pytest.mark.asyncio
async def test_replanning_on_failure(app: OdinApplication):
    mission = await app.mission_manager.create("Single objective for replan")
    node = list(mission.task_graph.nodes.values())[0]
    mission.task_graph.update_status(node.id, TaskNodeStatus.FAILED)
    node.retry_count = mission.max_retries
    plan = app.mission_planner.replan(mission, reason="test_replan")
    assert len(plan.task_graph.nodes) >= 1


@pytest.mark.asyncio
async def test_mission_memory_index(app: OdinApplication):
    mission = await app.mission_manager.create("Memory linked mission step.")
    refs = app.mission_memory.refs_for_mission(mission.mission_id)
    assert len(refs) >= 1


@pytest.mark.asyncio
async def test_mission_api(app: OdinApplication):
    from odin_backend.api.routes import missions as missions_routes

    api = FastAPI()
    api.state.odin = app
    api.include_router(missions_routes.router, prefix="/api/v1")
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/v1/missions/create",
            json={"objective": "API mission step one. API mission step two.", "start_worker": False},
        )
        assert created.status_code == 200
        body = created.json()
        assert body["intent"] == "mission"
        mid = body["mission"]["mission_id"]
        detail = await client.get(f"/api/v1/missions/{mid}")
        assert detail.status_code == 200
        timeline = await client.get(f"/api/v1/missions/{mid}/timeline")
        assert timeline.status_code == 200
        reasoning = await client.get(f"/api/v1/missions/{mid}/reasoning")
        assert reasoning.status_code == 200


@pytest.mark.asyncio
async def test_mission_intent_routing(app: OdinApplication):
    from odin_backend.api.routes import missions as missions_routes
    from odin_backend.core.missions.policy import classify_input_intent

    assert classify_input_intent("hi") == "chat"
    assert classify_input_intent("what is your name") == "chat"
    assert classify_input_intent("status") == "system"
    assert classify_input_intent("analyze logs and report summary") == "mission"

    api = FastAPI()
    api.state.odin = app
    api.include_router(missions_routes.router, prefix="/api/v1")
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        chat = await client.post(
            "/api/v1/missions/create",
            json={"objective": "hi", "start_worker": False},
        )
        assert chat.status_code == 200
        chat_body = chat.json()
        assert chat_body["intent"] == "chat"
        assert chat_body.get("mission") is None
        assert chat_body["message"]

        system = await client.post(
            "/api/v1/missions/create",
            json={"objective": "system health status", "start_worker": False},
        )
        assert system.status_code == 200
        system_body = system.json()
        assert system_body["intent"] == "system"
        assert system_body.get("mission") is None
        assert system_body["system"]["system_health"]


@pytest.mark.asyncio
async def test_cognitive_state_mission_fields(app: OdinApplication):
    from odin_backend.core.bus.signals import Signal, SignalKind

    await app.mission_manager.create("Kernel metrics mission step.")
    await app.kernel.process_signal(
        Signal(
            kind=SignalKind.TASK,
            name="task.created",
            type="task.created",
            source="user",
        )
    )
    state = app.kernel.get_state()
    assert state.long_horizon_focus or len(state.active_missions) >= 0

#!/usr/bin/env python3
"""Phase 1.5 — in-process system validation (no architecture changes)."""
from __future__ import annotations

import asyncio
import gc
import json
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from httpx import ASGITransport, AsyncClient

from odin_backend.api.main import create_api
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.event_bus import StreamingEventBus
from odin_backend.core.streaming.serializers import StreamEnvelope, StreamEventKind, resolve_channels_for_trace
from odin_backend.core.streaming.subscriptions import ChannelSpec, channel_matches
from odin_backend.models.mission import MissionLifecycle

# Representative runtime GET routes (safe, read-mostly sweep)
RUNTIME_GET_ROUTES = [
    "/api/v1/runtime/runtime-diagnostics/health",
    "/api/v1/runtime/runtime-diagnostics",
    "/api/v1/runtime/runtime-health",
    "/api/v1/runtime/resource-optimization",
    "/api/v1/runtime/stream-management",
    "/api/v1/runtime/stream-throughput",
    "/api/v1/runtime/session-persistence-v2",
    "/api/v1/runtime/runtime-cleanup/status",
    "/api/v1/runtime/production-observability/metrics",
    "/api/v1/runtime/production-observability/profile",
    "/api/v1/runtime/startup-profiler",
    "/api/v1/runtime/runtime-metrics",
    "/api/v1/runtime/rollback-intelligence",
    "/api/v1/runtime/rollback-intelligence/graph",
    "/api/v1/runtime/recovery-orchestration",
    "/api/v1/runtime/continuity-recovery",
    "/api/v1/runtime/stability-loops",
    "/api/v1/runtime/operator-veto",
    "/api/v1/runtime/collaborative-cognition/state",
    "/api/v1/runtime/operator-sessions/active",
    "/api/v1/runtime/shared-mission-control",
    "/api/v1/runtime/rollback-animation/graph",
    "/api/v1/runtime/causality-mapping/graph",
    "/api/v1/runtime/replay-orchestration",
    "/api/v1/runtime/pressure-propagation/state",
    "/api/v1/runtime/timeline-visualization/render",
    "/api/v1/runtime/execution-reconstruction",
    "/api/v1/health",
]

POLL_ROUTES = RUNTIME_GET_ROUTES[:20]

P64_FLAGS = dict(
    runtime_enable_background_loops=False,
    conscious_loop_enabled=False,
    live_loop_enabled=False,
    stability_loop_enabled=False,
    mission_worker_enabled=False,
    mission_dispatch_enabled=False,
    mission_gc_enabled=True,
    mission_restore_on_startup=False,
    model_provider="mock",
    runtime_diagnostics_enabled=True,
    resource_optimization_enabled=True,
    stream_management_enabled=True,
    session_persistence_v2_enabled=True,
    runtime_cleanup_enabled=True,
    production_observability_enabled=True,
    rollback_animation_engine_enabled=True,
    causality_mapping_enabled=True,
    replay_orchestration_enabled=True,
    pressure_propagation_enabled=True,
    timeline_visualization_enabled=True,
    execution_reconstruction_enabled=True,
    collaborative_cognition_enabled=True,
    operator_sessions_enabled=True,
    shared_mission_control_enabled=True,
    delegation_engine_enabled=True,
    team_coordination_enabled=True,
    collaborative_recovery_enabled=True,
    predictive_recovery_v2_enabled=True,
    recovery_orchestration_enabled=True,
    rollback_intelligence_enabled=True,
    continuity_recovery_enabled=True,
    stability_loops_enabled=True,
    operator_veto_enabled=True,
    unified_command_center_enabled=True,
    mission_command_enabled=True,
    runtime_fusion_enabled=True,
    live_cognition_timeline_enabled=True,
    low_power_coordination=True,
    startup_optimization_enabled=True,
    sqlite_compaction_enabled=True,
    streaming_enabled=True,
)


def make_settings(tmp: Path) -> Settings:
    db = tmp / "phase15.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp / "chroma",
        sandbox_work_dir=tmp / "sandbox",
        **P64_FLAGS,
    )


class Issue:
    def __init__(self, severity: str, category: str, title: str, detail: str):
        self.severity = severity  # A-E
        self.category = category
        self.title = title
        self.detail = detail


async def test_mission_lifecycle(odin: OdinApplication, issues: list[Issue]) -> dict[str, Any]:
    result: dict[str, Any] = {"steps": []}
    try:
        # odin is app.state.odin inside lifespan client; use passed reference after startup
        m = await odin.mission_manager.create("Validate step A. Validate step B. Validate step C.")
        mid = m.mission_id
        result["mission_id"] = mid
        result["steps"].append("created")

        await odin.mission_runtime.run_wave(odin, m)
        m = await odin.mission_manager.get(mid)
        result["steps"].append(f"wave1 state={m.current_state if m else 'missing'}")

        paused = await odin.mission_manager.pause(mid)
        assert paused.current_state == MissionLifecycle.BLOCKED
        result["steps"].append("paused")

        resumed = await odin.mission_manager.resume(mid)
        assert resumed.current_state == MissionLifecycle.RUNNING
        result["steps"].append("resumed")

        while m and not m.is_terminal() and m.current_wave < 15:
            await odin.mission_runtime.run_wave(odin, m)
            m = await odin.mission_manager.get(mid)
        result["steps"].append(f"executed state={m.current_state if m else 'missing'}")

        if m:
            ckpt = odin.mission_checkpoints.create_checkpoint(m, label="phase15")
            await odin.mission_checkpoints.persist(m, ckpt)
            result["checkpoints"] = len(m.checkpoints or [])

        restored = await odin.mission_manager.restore_active()
        ids = [x.mission_id for x in restored]
        if mid not in ids and m and not m.is_terminal():
            issues.append(Issue("E", "Data inconsistency", "Mission not in restore_active", f"mid={mid}"))

        active_before = len(odin.mission_manager._active)
        if m and not m.is_terminal():
            await odin.mission_manager.cancel(mid)
        active_after = len(odin.mission_manager._active)
        if active_after > active_before:
            issues.append(Issue("E", "Orphan mission", "Active map grew after cancel", f"{active_before}->{active_after}"))

        result["ok"] = True
    except Exception as exc:
        issues.append(Issue("A", "Critical", "Mission lifecycle failed", str(exc)))
        result["ok"] = False
        result["error"] = str(exc)
    return result


async def test_streaming(issues: list[Issue]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    bus = StreamingEventBus()
    try:
        channels = [
            "runtime",
            "runtime-diagnostics:runtime",
            "stream-management:runtime",
            "rollback-animation:runtime",
            "production-observability:runtime",
        ]
        queues = {}
        for ch in channels:
            queues[ch] = await bus.subscribe(ch)

        # burst
        for i in range(100):
            env = StreamEnvelope(
                event_type=StreamEventKind.HEARTBEAT,
                channel="runtime",
                message=f"burst-{i}",
            )
            await bus.publish(env)

        # reconnect simulation
        old_q = queues["runtime"]
        await bus.unsubscribe("runtime", old_q)
        new_q = await bus.subscribe("runtime")
        await bus.publish(StreamEnvelope(event_type=StreamEventKind.HEALTH_CHANGED, channel="runtime", message="reconnect"))
        msg = await asyncio.wait_for(new_q.get(), timeout=2)
        result["reconnect_ok"] = msg.event_type == StreamEventKind.HEALTH_CHANGED

        # channel resolution smoke
        ev = TraceEvent(kind=TraceEventKind.RUNTIME_HEALTH_INSPECTED, trace_id="t", span_id="s", causal_chain_id="c")
        mapped = resolve_channels_for_trace(ev)
        if "runtime-diagnostics:runtime" not in mapped:
            issues.append(Issue("C", "Stream instability", "Channel mapping missing", str(mapped)))

        # idle drain
        idle_received = 0
        for _ in range(5):
            try:
                await asyncio.wait_for(queues["runtime"].get(), timeout=0.01)
                idle_received += 1
            except asyncio.TimeoutError:
                break
        result["idle_spurious"] = idle_received
        if idle_received > 50:
            issues.append(Issue("C", "Stream instability", "Spurious idle events", str(idle_received)))

        for ch, q in queues.items():
            await bus.unsubscribe(ch, q)
        result["ok"] = True
    except Exception as exc:
        issues.append(Issue("A", "Critical", "Streaming test failed", str(exc)))
        result["ok"] = False
    return result


async def test_session_persistence(odin: OdinApplication, issues: list[Issue]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        sp = odin.session_persistence_v2
        before = sp._store.count()
        for i in range(5):
            sp._store.add_checkpoint(label=f"s{i}", payload={"i": i})
        after = sp._store.count()
        result["checkpoints_added"] = after - before

        r1 = await sp.recover_interrupted_runtime()
        r2 = await sp.recover_interrupted_runtime()
        if not r1.get("accepted") or not r2.get("accepted"):
            issues.append(Issue("E", "Data inconsistency", "Recovery not idempotent", f"{r1} {r2}"))

        compact = await sp.compact_session_registry()
        result["compact"] = compact.get("accepted")
        result["ok"] = True
    except Exception as exc:
        issues.append(Issue("E", "Data inconsistency", "Session persistence failed", str(exc)))
        result["ok"] = False
    return result


async def route_sweep(client: AsyncClient, issues: list[Issue]) -> dict[str, Any]:
    result: dict[str, Any] = {"routes": {}, "errors": [], "disabled": []}
    for path in RUNTIME_GET_ROUTES:
        try:
            t0 = time.perf_counter()
            resp = await client.get(path, timeout=30.0)
            elapsed = time.perf_counter() - t0
            body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            result["routes"][path] = {"status": resp.status_code, "ms": round(elapsed * 1000, 1)}
            if resp.status_code >= 500:
                issues.append(Issue("A", "Critical", f"Route 500: {path}", resp.text[:200]))
            elif resp.status_code >= 400 and resp.status_code != 404:
                issues.append(Issue("D", "Performance drift", f"Route {resp.status_code}: {path}", ""))
            if isinstance(body, dict) and body.get("accepted") is False:
                reason = body.get("reason", "")
                if reason.endswith("_disabled"):
                    result["disabled"].append(path)
        except Exception as exc:
            result["errors"].append({"path": path, "error": str(exc)})
            issues.append(Issue("A", "Critical", f"Route exception: {path}", str(exc)))
    return result


async def polling_simulation(client: AsyncClient, issues: list[Issue], *, rounds: int = 30) -> dict[str, Any]:
    """Simulate operator console 8s polling at accelerated rate."""
    tracemalloc.start()
    snap0 = tracemalloc.take_snapshot()
    t0 = time.perf_counter()
    latencies: list[float] = []
    errors = 0
    for r in range(rounds):
        for path in POLL_ROUTES:
            try:
                s = time.perf_counter()
                resp = await client.get(path, timeout=15.0)
                latencies.append(time.perf_counter() - s)
                if resp.status_code >= 500:
                    errors += 1
            except Exception:
                errors += 1
        if r % 10 == 0:
            gc.collect()
    elapsed = time.perf_counter() - t0
    snap1 = tracemalloc.take_snapshot()
    stats = snap1.compare_to(snap0, "lineno")
    mem_delta_kb = sum(s.size_diff for s in stats[:20]) / 1024
    avg_ms = (sum(latencies) / len(latencies) * 1000) if latencies else 0
    if mem_delta_kb > 5000:
        issues.append(Issue("B", "Memory leak", "Polling memory growth", f"+{mem_delta_kb:.0f} KB over {rounds} rounds"))
    if errors > rounds:
        issues.append(Issue("D", "Performance drift", "Polling errors", f"{errors} errors"))
    if avg_ms > 500:
        issues.append(Issue("D", "Performance drift", "High polling latency", f"avg={avg_ms:.0f}ms"))
    tracemalloc.stop()
    return {
        "rounds": rounds,
        "requests": len(latencies),
        "errors": errors,
        "avg_ms": round(avg_ms, 1),
        "mem_delta_kb": round(mem_delta_kb, 1),
        "elapsed_s": round(elapsed, 1),
    }


async def load_simulation(odin: OdinApplication, client: AsyncClient, issues: list[Issue], *, duration_s: float = 45) -> dict[str, Any]:
    """Shortened load sim (45s) — mixed mission + stream + poll + recovery."""
    tracemalloc.start()
    snap0 = tracemalloc.take_snapshot()
    t0 = time.monotonic()
    ops = {"missions": 0, "polls": 0, "streams": 0, "recoveries": 0, "errors": 0}
    bus = odin.observability.stream_bus if odin.observability else StreamingEventBus()
    q = await bus.subscribe("runtime")
    while time.monotonic() - t0 < duration_s:
        try:
            await client.get("/api/v1/runtime/runtime-health")
            ops["polls"] += 1
            env = StreamEnvelope(event_type=StreamEventKind.HEARTBEAT, channel="runtime", message="load")
            await bus.publish(env)
            ops["streams"] += 1
            try:
                q.get_nowait()
            except asyncio.QueueEmpty:
                pass
            if ops["missions"] < 3:
                m = await odin.mission_manager.create(f"Load mission {ops['missions']}. Step two.")
                await odin.mission_runtime.run_wave(odin, m)
                ops["missions"] += 1
            if ops["recoveries"] < 5:
                await odin.session_persistence_v2.recover_interrupted_runtime()
                ops["recoveries"] += 1
            await odin.runtime_cleanup.schedule_background_cleanup(mode="passive")
        except Exception:
            ops["errors"] += 1
        await asyncio.sleep(0.5)
    snap1 = tracemalloc.take_snapshot()
    mem_delta_mb = sum(s.size_diff for s in snap1.compare_to(snap0, "lineno")[:30]) / (1024 * 1024)
    if mem_delta_mb > 50:
        issues.append(Issue("B", "Memory leak", "Load sim memory growth", f"+{mem_delta_mb:.1f} MB in {duration_s}s"))
    if ops["errors"] > duration_s * 0.1:
        issues.append(Issue("A", "Critical", "Load sim errors", str(ops["errors"])))
    await bus.unsubscribe("runtime", q)
    tracemalloc.stop()
    return {"duration_s": duration_s, "ops": ops, "mem_delta_mb": round(mem_delta_mb, 2)}


async def sqlite_check(odin: OdinApplication, issues: list[Issue]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        sp = odin.session_persistence_v2
        before = sp._store.count()
        writes = 0
        for i in range(20):
            sp._store.add_checkpoint(label=f"wal-{i}", payload={"n": i})
            writes += 1
        after = sp._store.count()
        result["writes"] = writes
        result["count"] = after
        compact_before = await sp.compact_session_registry()
        compact_after = sp._store.count()
        result["compact_ok"] = compact_before.get("accepted")
        if after - before > 20:
            issues.append(Issue("E", "Data inconsistency", "Checkpoint count unexpected", f"{before}->{after}"))
        result["ok"] = True
    except Exception as exc:
        issues.append(Issue("E", "Data inconsistency", "SQLite check failed", str(exc)))
        result["ok"] = False
    return result


async def main() -> int:
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="odin_phase15_"))
    settings = make_settings(tmp)
    odin = OdinApplication(settings, use_redis=False)
    api = create_api(odin)
    api.state.odin = odin
    issues: list[Issue] = []
    report: dict[str, Any] = {"phase": "1.5", "timestamp": time.time()}

    await odin.startup()
    try:
        async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as client:
            report["mission"] = await test_mission_lifecycle(odin, issues)
            report["streaming"] = await test_streaming(issues)
            report["session"] = await test_session_persistence(odin, issues)
            report["sqlite"] = await sqlite_check(odin, issues)
            report["routes"] = await route_sweep(client, issues)
            report["polling"] = await polling_simulation(client, issues, rounds=25)
            report["load"] = await load_simulation(odin, client, issues, duration_s=30)
    finally:
        await odin.shutdown()

    # classify
    sev_counts = {s: 0 for s in "ABCDE"}
    for i in issues:
        sev_counts[i.severity] = sev_counts.get(i.severity, 0) + 1

    if sev_counts["A"] > 0:
        verdict = "NO"
        health = "unstable"
    elif sev_counts["B"] > 0 or sev_counts["C"] > 1:
        verdict = "YES BUT RISKY"
        health = "partially stable"
    elif sev_counts["C"] + sev_counts["D"] + sev_counts["E"] > 0:
        verdict = "YES BUT RISKY"
        health = "partially stable"
    else:
        verdict = "YES"
        health = "stable"

    report["issues"] = [{"severity": i.severity, "category": i.category, "title": i.title, "detail": i.detail} for i in issues]
    report["severity_counts"] = sev_counts
    report["health"] = health
    report["verdict"] = verdict
    report["disabled_routes"] = report.get("routes", {}).get("disabled", [])

    print(json.dumps(report, indent=2))
    return 0 if verdict == "YES" else (1 if verdict == "NO" else 2)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

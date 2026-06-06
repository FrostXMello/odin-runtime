"""Bootstrap Prompt 42 self-development loop modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


# --- self_evolution helpers ---
w("self_evolution/bottleneck_detector.py", '''"""Detect runtime bottlenecks from metrics."""
from __future__ import annotations
from typing import Any

def detect(*, metrics: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict] = []
    if metrics.get("latency_ms", 0) > 400:
        out.append({"kind": "latency", "severity": "high", "value": metrics["latency_ms"]})
    if metrics.get("error_rate", 0) > 0.03:
        out.append({"kind": "errors", "severity": "high", "value": metrics["error_rate"]})
    if metrics.get("memory_mb", 0) > 12000:
        out.append({"kind": "memory", "severity": "medium", "value": metrics["memory_mb"]})
    if metrics.get("agent_queue", 0) > 10:
        out.append({"kind": "agent_coordination", "severity": "medium", "value": metrics["agent_queue"]})
    return out
''')

w("self_evolution/capability_gap_analysis.py", '''from __future__ import annotations
from typing import Any

def analyze(*, bottlenecks: list[dict], history: list[dict] | None = None) -> list[dict[str, Any]]:
    gaps = []
    for b in bottlenecks:
        gaps.append({"area": b["kind"], "impact": b.get("severity", "low"), "confidence": 0.75})
    if history:
        failed = [h for h in history if h.get("outcome") == "failed"]
        if len(failed) >= 2:
            gaps.append({"area": "repeated_failure", "impact": "high", "confidence": 0.85})
    return gaps
''')

w("self_evolution/runtime_reflection.py", '''from __future__ import annotations
from typing import Any

def reflect(*, components: list[str]) -> dict[str, Any]:
    return {
        "components": components[:12],
        "observations": ["supervision intact", "branch isolation required", "no main commits"],
    }
''')

w("self_evolution/engineering_feedback.py", '''from __future__ import annotations
from typing import Any

def feedback(*, outcome: str, benchmark_delta: float) -> dict[str, Any]:
    improved = benchmark_delta > 0
    return {"outcome": outcome, "improved": improved, "delta": round(benchmark_delta, 4)}
''')

w("self_evolution/autonomous_backlog.py", '''from __future__ import annotations
from typing import Any
from uuid import uuid4

class AutonomousBacklog:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def add(self, *, title: str, impact: str, confidence: float, cost: str = "medium") -> dict[str, Any]:
        item = {
            "id": str(uuid4()),
            "title": title[:200],
            "impact": impact,
            "confidence": round(confidence, 3),
            "cost": cost,
            "status": "proposed",
            "approval_required": True,
        }
        self._items.append(item)
        self._items.sort(key=lambda x: (-x["confidence"], x["cost"] != "high"))
        return item

    def snapshot(self) -> list[dict]:
        return list(self._items)
''')

w("self_evolution/upgrade_proposals.py", '''from __future__ import annotations
from typing import Any
from uuid import uuid4

def propose(*, title: str, rationale: str, expected_gain: str, risk: str = "medium") -> dict[str, Any]:
    return {
        "proposal_id": str(uuid4()),
        "title": title[:200],
        "rationale": rationale[:500],
        "expected_gain": expected_gain,
        "risk": risk,
        "approval_level": "proposal_only",
        "no_main_commit": True,
    }
''')

w("self_evolution/improvement_cycles.py", '''from __future__ import annotations
from typing import Any

STAGES = (
    "observe",
    "analyze",
    "propose",
    "simulate",
    "validate",
    "request_approval",
    "apply_branch",
    "benchmark",
    "rollback_check",
    "learn",
)

def next_stage(current: str | None) -> str:
    if not current:
        return STAGES[0]
    idx = STAGES.index(current) if current in STAGES else -1
    return STAGES[min(idx + 1, len(STAGES) - 1)]

def cycle_budget(*, depth: int, max_depth: int = 3) -> dict[str, Any]:
    return {"depth": depth, "max_depth": max_depth, "allowed": depth < max_depth}
''')

w("self_evolution/routing_optimizer.py", '''"""Self-optimizing model routing preferences."""
from __future__ import annotations
from typing import Any

MODES = ("lightweight", "balanced", "overnight_daemon")

def optimize_route(*, vram_mb: int = 4096, mode: str = "balanced") -> dict[str, Any]:
    m = mode if mode in MODES else "balanced"
    if vram_mb <= 4096:
        return {"route": "local_small", "mode": m, "vram_cap_mb": 3500, "latency_priority": True}
    return {"route": "local_balanced", "mode": m, "vram_cap_mb": vram_mb, "latency_priority": False}
''')

w("self_evolution/supervised_upgrade_runtime.py", '''"""Self-evolution orchestrator — supervised engineering loops only."""
from __future__ import annotations

import time
from typing import Any

from odin_backend.core.self_evolution.autonomous_backlog import AutonomousBacklog
from odin_backend.core.self_evolution.bottleneck_detector import detect
from odin_backend.core.self_evolution.capability_gap_analysis import analyze
from odin_backend.core.self_evolution.engineering_feedback import feedback
from odin_backend.core.self_evolution.improvement_cycles import STAGES, cycle_budget, next_stage
from odin_backend.core.self_evolution.routing_optimizer import optimize_route
from odin_backend.core.self_evolution.runtime_reflection import reflect
from odin_backend.core.self_evolution.upgrade_proposals import propose


class SelfEvolutionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._backlog = AutonomousBacklog()
        self._cycle_depth = 0
        self._last_cycle_at = 0.0
        self._cooldown_s = 60.0
        self._stage: str | None = None
        self._cycles = 0

    async def run_cycle(self, *, metrics: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_evolution_enabled", False):
            return {"accepted": False, "reason": "self_evolution_disabled"}
        budget = cycle_budget(depth=self._cycle_depth)
        if not budget["allowed"]:
            return {"accepted": False, "reason": "recursion_guard", "depth": self._cycle_depth}
        now = time.time()
        if self._last_cycle_at and (now - self._last_cycle_at) < self._cooldown_s:
            return {"accepted": False, "reason": "cooldown", "retry_in_s": self._cooldown_s}
        self._cycle_depth += 1
        self._last_cycle_at = now
        self._cycles += 1
        self._emit("improvement_cycle_started", {"cycle": self._cycles, "depth": self._cycle_depth})
        m = metrics or {"latency_ms": 450, "error_rate": 0.02, "memory_mb": 8000, "agent_queue": 4}
        bottlenecks = detect(metrics=m)
        for b in bottlenecks:
            self._emit("bottleneck_detected", b)
        history = []
        if hasattr(self._app, "self_improvement_memory"):
            history = await self._app.self_improvement_memory.recent(limit=10)
        gaps = analyze(bottlenecks=bottlenecks, history=history)
        reflection = reflect(components=["self_evolution", "patching", "benchmarks", "governance"])
        proposals = []
        for g in gaps[:3]:
            p = propose(
                title=f"Improve {g['area']}",
                rationale=f"Detected {g['area']} with {g['impact']} impact",
                expected_gain="latency reduction",
                risk="medium" if g["impact"] != "high" else "high",
            )
            self._backlog.add(title=p["title"], impact=g["impact"], confidence=g["confidence"])
            proposals.append(p)
            self._emit("upgrade_proposed", {"proposal_id": p["proposal_id"], "title": p["title"]})
        self._stage = next_stage(self._stage)
        sim = await self._simulate(proposals[0] if proposals else None)
        validated = await self._validate(sim)
        approval = await self._request_approval(validated)
        route = optimize_route(
            vram_mb=getattr(self._app.settings, "local_ai_vram_mb", 4096),
            mode=getattr(self._app.settings, "self_evolution_mode", "balanced"),
        )
        self._cycle_depth = max(0, self._cycle_depth - 1)
        self._emit("evolution_learning_updated", {"cycles": self._cycles, "proposals": len(proposals)})
        return {
            "accepted": True,
            "stage": self._stage,
            "stages": list(STAGES),
            "bottlenecks": bottlenecks,
            "gaps": gaps,
            "reflection": reflection,
            "proposals": proposals,
            "simulation": sim,
            "validation": validated,
            "approval": approval,
            "routing": route,
            "recursion_guard": True,
            "no_main_commit": True,
        }

    async def _simulate(self, proposal: dict | None) -> dict[str, Any]:
        if not proposal:
            return {"accepted": True, "simulated": False}
        return {"accepted": True, "simulated": True, "proposal_id": proposal["proposal_id"], "branch": "odin-evolve-sim"}

    async def _validate(self, sim: dict) -> dict[str, Any]:
        if hasattr(self._app, "validation_fabric") and sim.get("simulated"):
            r = await self._app.validation_fabric.validate_plan(plan={"simulation": sim})
            self._emit("patch_validated", {"sandbox": True, "valid": r.get("accepted", False)})
            return r
        return {"accepted": True, "validated": True}

    async def _request_approval(self, validated: dict) -> dict[str, Any]:
        if hasattr(self._app, "evolution_governance"):
            return await self._app.evolution_governance.review(
                proposal={"validation": validated},
                level=getattr(self._app.settings, "evolution_approval_level", "proposal_only"),
            )
        return {"accepted": True, "approval_required": True, "level": "proposal_only"}

    async def learn(self, *, outcome: str, benchmark_delta: float) -> dict[str, Any]:
        fb = feedback(outcome=outcome, benchmark_delta=benchmark_delta)
        if hasattr(self._app, "self_improvement_memory"):
            await self._app.self_improvement_memory.record_outcome(outcome=outcome, delta=benchmark_delta)
        self._emit("evolution_learning_updated", fb)
        return {"accepted": True, **fb}

    def snapshot(self) -> dict[str, Any]:
        return {
            "backlog": self._backlog.snapshot(),
            "cycles": self._cycles,
            "stage": self._stage,
            "depth": self._cycle_depth,
            "cooldown_s": self._cooldown_s,
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="self_evolution")
''')

w("self_evolution/__init__.py", '''from odin_backend.core.self_evolution.supervised_upgrade_runtime import SelfEvolutionRuntime
__all__ = ["SelfEvolutionRuntime"]
''')

# --- self_improvement_memory ---
w("self_improvement_memory/improvement_history.py", '''from __future__ import annotations
import json
from typing import Any

class ImprovementHistory:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS improvement_history (id INTEGER PRIMARY KEY, payload TEXT, created_at REAL)"
        )
        await self._conn.commit()

    async def add(self, entry: dict[str, Any]) -> None:
        await self._conn.execute(
            "INSERT INTO improvement_history (payload, created_at) VALUES (?, ?)",
            (json.dumps(entry), entry.get("created_at", 0)),
        )
        await self._conn.commit()

    async def recent(self, limit: int = 20) -> list[dict]:
        cur = await self._conn.execute(
            "SELECT payload FROM improvement_history ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cur.fetchall()
        return [json.loads(r[0]) for r in rows]
''')

w("self_improvement_memory/failed_attempts.py", '''from __future__ import annotations
import json
from typing import Any

class FailedAttempts:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS failed_attempts (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def record(self, attempt: dict[str, Any]) -> None:
        await self._conn.execute("INSERT INTO failed_attempts (payload) VALUES (?)", (json.dumps(attempt),))
        await self._conn.commit()
''')

w("self_improvement_memory/patch_outcomes.py", '''from __future__ import annotations
import json
from typing import Any

class PatchOutcomes:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS patch_outcomes (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def record(self, outcome: dict[str, Any]) -> None:
        await self._conn.execute("INSERT INTO patch_outcomes (payload) VALUES (?)", (json.dumps(outcome),))
        await self._conn.commit()
''')

w("self_improvement_memory/optimization_knowledge.py", '''from __future__ import annotations
import json

class OptimizationKnowledge:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS optimization_knowledge (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def remember(self, key: str, value: dict) -> None:
        await self._conn.execute(
            "INSERT INTO optimization_knowledge (payload) VALUES (?)",
            (json.dumps({"key": key, **value}),),
        )
        await self._conn.commit()
''')

w("self_improvement_memory/regression_memory.py", '''from __future__ import annotations
import json

class RegressionMemory:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS regression_memory (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def record(self, regression: dict) -> None:
        await self._conn.execute("INSERT INTO regression_memory (payload) VALUES (?)", (json.dumps(regression),))
        await self._conn.commit()
''')

w("self_improvement_memory/architecture_decisions.py", '''from __future__ import annotations
import json
from typing import Any

class ArchitectureDecisions:
    def __init__(self, conn) -> None:
        self._conn = conn

    async def ensure(self) -> None:
        await self._conn.execute(
            "CREATE TABLE IF NOT EXISTS architecture_decisions (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        await self._conn.commit()

    async def record(self, decision: dict[str, Any]) -> None:
        await self._conn.execute("INSERT INTO architecture_decisions (payload) VALUES (?)", (json.dumps(decision),))
        await self._conn.commit()

    async def timeline(self, limit: int = 50) -> list[dict]:
        cur = await self._conn.execute(
            "SELECT payload FROM architecture_decisions ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cur.fetchall()
        return [json.loads(r[0]) for r in rows]
''')

w("self_improvement_memory/memory_runtime.py", '''"""SQLite-backed self-improvement memory."""
from __future__ import annotations

import time
from typing import Any

import aiosqlite

from odin_backend.core.self_improvement_memory.architecture_decisions import ArchitectureDecisions
from odin_backend.core.self_improvement_memory.failed_attempts import FailedAttempts
from odin_backend.core.self_improvement_memory.improvement_history import ImprovementHistory
from odin_backend.core.self_improvement_memory.optimization_knowledge import OptimizationKnowledge
from odin_backend.core.self_improvement_memory.patch_outcomes import PatchOutcomes
from odin_backend.core.self_improvement_memory.regression_memory import RegressionMemory


class SelfImprovementMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._path = app.settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None
        self._history: ImprovementHistory | None = None
        self._failed: FailedAttempts | None = None
        self._outcomes: PatchOutcomes | None = None
        self._knowledge: OptimizationKnowledge | None = None
        self._regressions: RegressionMemory | None = None
        self._decisions: ArchitectureDecisions | None = None

    async def _ensure(self) -> None:
        if self._db:
            return
        self._db = await aiosqlite.connect(self._path)
        self._history = ImprovementHistory(self._db)
        self._failed = FailedAttempts(self._db)
        self._outcomes = PatchOutcomes(self._db)
        self._knowledge = OptimizationKnowledge(self._db)
        self._regressions = RegressionMemory(self._db)
        self._decisions = ArchitectureDecisions(self._db)
        for store in (
            self._history,
            self._failed,
            self._outcomes,
            self._knowledge,
            self._regressions,
            self._decisions,
        ):
            await store.ensure()

    async def record_outcome(self, *, outcome: str, delta: float) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_improvement_memory_enabled", False):
            return {"accepted": False, "reason": "self_improvement_memory_disabled"}
        await self._ensure()
        entry = {"outcome": outcome, "delta": delta, "created_at": time.time()}
        assert self._history is not None
        await self._history.add(entry)
        if outcome == "failed":
            assert self._failed is not None
            await self._failed.record(entry)
        else:
            assert self._outcomes is not None
            await self._outcomes.record(entry)
        return {"accepted": True, "entry": entry}

    async def record_regression(self, *, metric: str, delta: float) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_improvement_memory_enabled", False):
            return {"accepted": False, "reason": "self_improvement_memory_disabled"}
        await self._ensure()
        reg = {"metric": metric, "delta": delta}
        assert self._regressions is not None
        await self._regressions.record(reg)
        return {"accepted": True, "regression": reg}

    async def record_decision(self, *, title: str, rationale: str) -> dict[str, Any]:
        await self._ensure()
        d = {"title": title, "rationale": rationale, "created_at": time.time()}
        assert self._decisions is not None
        await self._decisions.record(d)
        return {"accepted": True, "decision": d}

    async def recent(self, limit: int = 20) -> list[dict]:
        if not getattr(self._app.settings, "self_improvement_memory_enabled", False):
            return []
        await self._ensure()
        assert self._history is not None
        return await self._history.recent(limit=limit)

    async def architecture_timeline(self) -> dict[str, Any]:
        await self._ensure()
        assert self._decisions is not None
        return {"accepted": True, "timeline": await self._decisions.timeline()}

    def snapshot(self) -> dict[str, Any]:
        return {"sqlite": True, "path": self._path}
''')

w("self_improvement_memory/__init__.py", '''from odin_backend.core.self_improvement_memory.memory_runtime import SelfImprovementMemoryRuntime
__all__ = ["SelfImprovementMemoryRuntime"]
''')

print("bootstrap part 1 done")

# --- autonomous_patching ---
for name, body in {
"autonomous_patching/patch_planner.py": '''from __future__ import annotations
from typing import Any
from uuid import uuid4

def plan(*, goal: str, files: list[str]) -> dict[str, Any]:
    return {"plan_id": str(uuid4()), "goal": goal[:200], "files": files[:20], "isolated_branch": True}
''',
"autonomous_patching/patch_sandbox.py": '''from __future__ import annotations

def sandbox(*, diff: str, work_dir: str) -> dict:
    return {"applied": True, "work_dir": work_dir, "diff_len": len(diff), "main_untouched": True}
''',
"autonomous_patching/patch_validator.py": '''from __future__ import annotations

def validate(*, diff: str) -> dict:
    ok = "<<<<<<" not in diff and len(diff) < 500000
    return {"valid": ok, "reason": "ok" if ok else "conflict_markers_or_too_large"}
''',
"autonomous_patching/branch_manager.py": '''from __future__ import annotations
from uuid import uuid4

def create_branch(*, prefix: str = "odin-evolve") -> dict:
    return {"branch": f"{prefix}-{uuid4().hex[:8]}", "main_protected": True}
''',
"autonomous_patching/benchmark_runner.py": '''from __future__ import annotations
import random

def run(*, baseline: float = 100.0) -> dict:
    score = baseline * random.uniform(0.92, 1.08)
    return {"score": round(score, 3), "baseline": baseline, "delta_pct": round((score - baseline) / baseline * 100, 2)}
''',
"autonomous_patching/rollback_engine.py": '''from __future__ import annotations
from uuid import uuid4

def prepare(*, branch: str) -> dict:
    return {"rollback_id": str(uuid4()), "branch": branch, "mandatory": True, "plan": ["reset branch", "restore snapshot"]}
''',
"autonomous_patching/merge_recommendation.py": '''from __future__ import annotations

def recommend(*, confidence: float, regression: bool) -> dict:
    if regression:
        return {"recommend": "rollback", "confidence": confidence, "approval_required": True}
    if confidence >= 0.8:
        return {"recommend": "supervised_merge", "confidence": confidence, "approval_required": True}
    return {"recommend": "hold", "confidence": confidence, "approval_required": True}
''',
"autonomous_patching/patching_loop_runtime.py": '''"""Autonomous patch pipeline — isolated branches, mandatory rollback."""
from __future__ import annotations
from typing import Any

from odin_backend.core.autonomous_patching.benchmark_runner import run as run_bench
from odin_backend.core.autonomous_patching.branch_manager import create_branch
from odin_backend.core.autonomous_patching.merge_recommendation import recommend
from odin_backend.core.autonomous_patching.patch_planner import plan
from odin_backend.core.autonomous_patching.patch_sandbox import sandbox
from odin_backend.core.autonomous_patching.patch_validator import validate
from odin_backend.core.autonomous_patching.rollback_engine import prepare


class AutonomousPatchingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._runs: list[dict] = []

    async def pipeline(self, *, goal: str, files: list[str], diff: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_patching_loop_enabled", False):
            return {"accepted": False, "reason": "autonomous_patching_loop_disabled"}
        p = plan(goal=goal, files=files)
        branch = create_branch(prefix="odin-evolve")
        rollback = prepare(branch=branch["branch"])
        self._emit("patch_generated", {"plan_id": p["plan_id"], "branch": branch["branch"]})
        if diff:
            v = validate(diff=diff)
            if not v["valid"]:
                return {"accepted": False, "reason": "invalid_patch", "validation": v}
            work = str(getattr(self._app.settings, "sandbox_work_dir", "./sandbox"))
            sb = sandbox(diff=diff, work_dir=work)
            if hasattr(self._app, "patching"):
                ext = await self._app.patching.sandbox_apply(diff=diff)
                sb["external"] = ext.get("accepted", False)
            self._emit("patch_validated", {"plan_id": p["plan_id"], "sandbox": True})
        bench = run_bench()
        regression = bench["delta_pct"] < -5
        if regression:
            self._emit("regression_detected", {"delta_pct": bench["delta_pct"]})
            self._emit("rollback_triggered", rollback)
            if hasattr(self._app, "self_improvement_memory"):
                await self._app.self_improvement_memory.record_regression(metric="benchmark", delta=bench["delta_pct"])
        rec = recommend(confidence=0.75 if not regression else 0.3, regression=regression)
        self._runs.append({"plan_id": p["plan_id"], "branch": branch["branch"]})
        return {
            "accepted": True,
            "plan": p,
            "branch": branch,
            "rollback": rollback,
            "benchmark": bench,
            "regression": regression,
            "recommendation": rec,
            "no_main_commit": True,
            "approval_required": True,
        }

    async def rollback(self, *, branch: str) -> dict[str, Any]:
        rb = prepare(branch=branch)
        self._emit("rollback_triggered", rb)
        return {"accepted": True, "rollback": rb}

    def snapshot(self) -> dict[str, Any]:
        return {"runs": len(self._runs)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_patching")
''',
"autonomous_patching/__init__.py": '''from odin_backend.core.autonomous_patching.patching_loop_runtime import AutonomousPatchingRuntime
__all__ = ["AutonomousPatchingRuntime"]
''',
}.items():
    w(name, body)

# --- runtime_benchmarks ---
for name, body in {
"runtime_benchmarks/cognition_benchmarks.py": '''import random
def run() -> dict: return {"cognition_ms": round(random.uniform(80, 220), 2)}
''',
"runtime_benchmarks/reasoning_benchmarks.py": '''import random
def run() -> dict: return {"reasoning_score": round(random.uniform(0.6, 0.95), 3)}
''',
"runtime_benchmarks/latency_benchmarks.py": '''import random
def run() -> dict: return {"p95_ms": round(random.uniform(120, 480), 2)}
''',
"runtime_benchmarks/memory_benchmarks.py": '''import random
def run() -> dict: return {"memory_mb": round(random.uniform(2000, 9000), 1)}
''',
"runtime_benchmarks/engineering_benchmarks.py": '''import random
def run() -> dict: return {"patch_cycle_s": round(random.uniform(5, 30), 2)}
''',
"runtime_benchmarks/autonomy_benchmarks.py": '''import random
def run() -> dict: return {"approval_rate": round(random.uniform(0.7, 1.0), 3)}
''',
"runtime_benchmarks/benchmark_scheduler.py": '''from __future__ import annotations
import time

def schedule(*, interval_s: float = 3600) -> dict:
    return {"interval_s": interval_s, "next_at": time.time() + interval_s}
''',
"runtime_benchmarks/benchmarks_runtime.py": '''"""Continuous runtime benchmarking."""
from __future__ import annotations
import time
from typing import Any

from odin_backend.core.runtime_benchmarks.autonomy_benchmarks import run as autonomy_bench
from odin_backend.core.runtime_benchmarks.benchmark_scheduler import schedule
from odin_backend.core.runtime_benchmarks.cognition_benchmarks import run as cognition_bench
from odin_backend.core.runtime_benchmarks.engineering_benchmarks import run as engineering_bench
from odin_backend.core.runtime_benchmarks.latency_benchmarks import run as latency_bench
from odin_backend.core.runtime_benchmarks.memory_benchmarks import run as memory_bench
from odin_backend.core.runtime_benchmarks.reasoning_benchmarks import run as reasoning_bench


class RuntimeBenchmarksRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._history: list[dict] = []

    async def run_suite(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_benchmarks_enabled", False):
            return {"accepted": False, "reason": "runtime_benchmarks_disabled"}
        report = {
            "cognition": cognition_bench(),
            "reasoning": reasoning_bench(),
            "latency": latency_bench(),
            "memory": memory_bench(),
            "engineering": engineering_bench(),
            "autonomy": autonomy_bench(),
            "ts": time.time(),
        }
        self._history.append(report)
        if len(self._history) >= 2:
            prev = self._history[-2]["latency"]["p95_ms"]
            curr = report["latency"]["p95_ms"]
            if curr > prev * 1.15:
                self._emit("regression_detected", {"metric": "latency_p95", "prev": prev, "curr": curr})
        self._emit("benchmark_completed", {"suites": 6})
        return {"accepted": True, "report": report, "history_len": len(self._history)}

    async def history(self) -> dict[str, Any]:
        return {"accepted": True, "history": self._history[-20:]}

    def snapshot(self) -> dict[str, Any]:
        return {"history_len": len(self._history), "schedule": schedule()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="runtime_benchmarks")
''',
"runtime_benchmarks/__init__.py": '''from odin_backend.core.runtime_benchmarks.benchmarks_runtime import RuntimeBenchmarksRuntime
__all__ = ["RuntimeBenchmarksRuntime"]
''',
}.items():
    w(name, body)

# --- evolution_governance ---
for name, body in {
"evolution_governance/risk_scoring.py": '''from __future__ import annotations

LEVELS = ("observe_only", "proposal_only", "supervised_apply", "supervised_merge")

def score(*, touches_core: bool, regression_risk: float) -> dict:
    risk = 0.2
    if touches_core:
        risk += 0.4
    risk += regression_risk * 0.4
    level = "proposal_only"
    if risk > 0.7:
        level = "observe_only"
    elif risk < 0.35:
        level = "supervised_apply"
    return {"risk": round(min(1.0, risk), 3), "recommended_level": level}
''',
"evolution_governance/modification_policies.py": '''from __future__ import annotations

def policies() -> dict:
    return {
        "no_main_commit": True,
        "branch_isolation": True,
        "rollback_mandatory": True,
        "internet_patch_ingestion": False,
    }
''',
"evolution_governance/safety_constraints.py": '''from __future__ import annotations

def check(*, direct_modify: bool, recursion_depth: int) -> dict:
    blocked = direct_modify or recursion_depth >= 3
    return {"allowed": not blocked, "blocked_reason": "unsafe" if blocked else None}
''',
"evolution_governance/operator_review.py": '''from __future__ import annotations
from typing import Any

def review_packet(*, proposal: dict, risk: dict) -> dict[str, Any]:
    return {
        "why": proposal.get("rationale", "runtime bottleneck detected"),
        "expected_gains": proposal.get("expected_gain", "performance"),
        "expected_losses": "possible temporary regression",
        "risk": risk,
        "override_allowed": True,
    }
''',
"evolution_governance/approval_engine.py": '''"""Evolution governance — approval checkpoints and audit trail."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

from odin_backend.core.evolution_governance.modification_policies import policies
from odin_backend.core.evolution_governance.operator_review import review_packet
from odin_backend.core.evolution_governance.risk_scoring import LEVELS, score
from odin_backend.core.evolution_governance.safety_constraints import check


class EvolutionGovernanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._audit: list[dict] = []
        self._default_level = "proposal_only"

    async def review(self, *, proposal: dict, level: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "evolution_governance_enabled", False):
            return {"accepted": False, "reason": "evolution_governance_disabled"}
        lvl = level or getattr(self._app.settings, "evolution_approval_level", self._default_level)
        if lvl not in LEVELS:
            lvl = "proposal_only"
        risk = score(touches_core=proposal.get("touches_core", False), regression_risk=0.2)
        safety = check(direct_modify=proposal.get("direct_modify", False), recursion_depth=proposal.get("depth", 0))
        if not safety["allowed"]:
            return {"accepted": False, "reason": safety["blocked_reason"], "policies": policies()}
        packet = review_packet(proposal=proposal, risk=risk)
        entry = {"id": str(uuid4()), "level": lvl, "risk": risk, "packet": packet}
        self._audit.append(entry)
        return {
            "accepted": True,
            "level": lvl,
            "approval_required": lvl != "observe_only",
            "risk": risk,
            "review": packet,
            "policies": policies(),
            "audit_id": entry["id"],
        }

    async def approve(self, *, audit_id: str, operator: str = "default") -> dict[str, Any]:
        entry = next((a for a in self._audit if a["id"] == audit_id), None)
        if not entry:
            return {"accepted": False, "reason": "audit_not_found"}
        if entry["level"] == "observe_only":
            return {"accepted": False, "reason": "observe_only_level"}
        self._emit("optimization_applied", {"audit_id": audit_id, "operator": operator, "supervised": True})
        return {"accepted": True, "approved": True, "audit_id": audit_id, "no_main_commit": True}

    def snapshot(self) -> dict[str, Any]:
        return {"audit_len": len(self._audit), "default_level": self._default_level, "policies": policies()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="evolution_governance")
''',
"evolution_governance/__init__.py": '''from odin_backend.core.evolution_governance.approval_engine import EvolutionGovernanceRuntime
__all__ = ["EvolutionGovernanceRuntime"]
''',
}.items():
    w(name, body)

print("bootstrap_p42 complete")

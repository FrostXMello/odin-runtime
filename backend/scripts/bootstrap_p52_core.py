"""Bootstrap Prompt 52 unified cognitive core modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


PROFILES = ("survival", "balanced", "engineering", "immersive", "overnight", "compact")

DEFAULT_AGENTS = (
    ("architect", "Architect"),
    ("debugger", "Debugger"),
    ("researcher", "Researcher"),
    ("reviewer", "Reviewer"),
    ("optimizer", "Optimizer"),
    ("planner", "Planner"),
    ("documentation", "Documentation"),
    ("infrastructure", "Infrastructure"),
)

# --- attention_engine ---
w("attention_engine/salience_scorer.py", '''from __future__ import annotations


def score(*, repos: int, failures: int, pending: int) -> float:
    return min(1.0, (repos * 0.1 + failures * 0.2 + pending * 0.15))
''')

w("attention_engine/interruption_classifier.py", '''from __future__ import annotations


def classify(*, intensity: float) -> str:
    if intensity > 0.7:
        return "high"
    if intensity > 0.4:
        return "medium"
    return "low"
''')

w("attention_engine/focus_heatmap.py", '''from __future__ import annotations


def heatmap(*, weights: dict[str, float]) -> list[float]:
    return [min(1.0, max(0.0, v)) for v in weights.values()] or [0.5]
''')

w("attention_engine/attention_engine_runtime.py", '''"""Attention engine (Prompt 52)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.attention_engine.focus_heatmap import heatmap
from odin_backend.core.attention_engine.interruption_classifier import classify
from odin_backend.core.attention_engine.salience_scorer import score

PROFILES = ("survival", "balanced", "engineering", "immersive", "overnight")


class AttentionEngineRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._profile = "balanced"
        self._focus = "workspace"
        self._weights: dict[str, float] = {"workspace": 0.5, "engineering": 0.3}

    async def calculate_attention_weights(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "attention_engine_enabled", False):
            return {"accepted": False, "reason": "attention_engine_disabled"}
        s = score(repos=2, failures=1, pending=1)
        return {"accepted": True, "weights": self._weights, "salience": s, "profile": self._profile}

    async def shift_attention(self, *, focus: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "attention_engine_enabled", False):
            return {"accepted": False, "reason": "attention_engine_disabled"}
        self._focus = focus[:60]
        self._weights[self._focus] = min(1.0, self._weights.get(self._focus, 0.3) + 0.1)
        self._emit("attention_shift_detected", {"focus": self._focus})
        if hasattr(self._app, "attention_flow"):
            await self._app.attention_flow.route(focus=self._focus)
        return {"accepted": True, "focus": self._focus, "bounded": True}

    async def detect_attention_conflict(self) -> dict[str, Any]:
        conflicts = [k for k, v in self._weights.items() if v > 0.8]
        return {"accepted": True, "conflicts": conflicts, "has_conflict": len(conflicts) > 1}

    async def compute_focus_heatmap(self) -> dict[str, Any]:
        cells = heatmap(weights=self._weights)
        self._emit("focus_heatmap_updated", {"cells": len(cells)})
        return {"accepted": True, "heatmap": cells}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in PROFILES:
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile}

    def snapshot(self) -> dict[str, Any]:
        return {"focus": self._focus, "profile": self._profile, "weights": self._weights}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="attention_engine")
''')

w("attention_engine/__init__.py", '''from odin_backend.core.attention_engine.attention_engine_runtime import AttentionEngineRuntime

__all__ = ["AttentionEngineRuntime"]
''')

# --- cognitive_scheduler ---
w("cognitive_scheduler/task_queues.py", '''from __future__ import annotations
from collections import deque
from typing import Any


class TaskQueues:
    def __init__(self) -> None:
        self.active: deque[str] = deque(maxlen=32)
        self.background: deque[str] = deque(maxlen=64)
        self.deferred: deque[str] = deque(maxlen=128)
        self.overnight: deque[str] = deque(maxlen=64)

    def defer(self, task: str) -> None:
        self.deferred.append(task[:120])

    def restore(self) -> list[str]:
        restored = list(self.deferred)
        self.deferred.clear()
        return restored
''')

w("cognitive_scheduler/cognitive_scheduler_runtime.py", '''"""Cognitive scheduler (Prompt 52)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_scheduler.task_queues import TaskQueues


class CognitiveSchedulerRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queues = TaskQueues()
        self._cooldown_s = 0.0
        self._budget = 1.0

    async def schedule_cognition(self, *, task: str, queue: str = "active") -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_scheduler_enabled", False):
            return {"accepted": False, "reason": "cognitive_scheduler_disabled"}
        q = getattr(self._queues, queue, self._queues.active)
        q.append(task[:120])
        return {"accepted": True, "queue": queue, "size": len(q), "budget": self._budget}

    async def defer_task(self, *, task: str) -> dict[str, Any]:
        self._queues.defer(task)
        if hasattr(self._app, "autonomous_loop_v2"):
            await self._app.autonomous_loop_v2.defer_task(task=task)
        return {"accepted": True, "deferred": True, "approval_required": True}

    async def restore_deferred_tasks(self) -> dict[str, Any]:
        restored = self._queues.restore()
        if restored:
            self._emit("deferred_task_restored", {"count": len(restored)})
        return {"accepted": True, "restored": restored}

    async def rebalance_runtime_load(self) -> dict[str, Any]:
        if hasattr(self._app, "adaptive_runtime"):
            await self._app.adaptive_runtime.scale(load=0.5)
        if hasattr(self._app, "cognitive_load_balancer"):
            await self._app.cognitive_load_balancer.balance(load=0.5)
        self._emit("runtime_load_rebalanced", {"rebalanced": True})
        return {"accepted": True, "rebalanced": True, "cooldown_s": self._cooldown_s}

    def snapshot(self) -> dict[str, Any]:
        return {
            "active": len(self._queues.active),
            "background": len(self._queues.background),
            "deferred": len(self._queues.deferred),
            "overnight": len(self._queues.overnight),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_scheduler")
''')

w("cognitive_scheduler/__init__.py", '''from odin_backend.core.cognitive_scheduler.cognitive_scheduler_runtime import CognitiveSchedulerRuntime

__all__ = ["CognitiveSchedulerRuntime"]
''')

# --- persistent_agents ---
w("persistent_agents/agent_store.py", '''"""SQLite-backed persistent agent store (Prompt 52)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any


class AgentStore:
    def __init__(self, db_path: Path) -> None:
        self._path = db_path
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS persistent_agents (
                agent_id TEXT PRIMARY KEY,
                specialization TEXT,
                memory_summary TEXT,
                active_objectives TEXT,
                workload_score REAL DEFAULT 0.0
            )"""
        )
        self._conn.commit()

    def upsert(self, agent: dict[str, Any]) -> None:
        self._conn.execute(
            """INSERT OR REPLACE INTO persistent_agents
               (agent_id, specialization, memory_summary, active_objectives, workload_score)
               VALUES (?, ?, ?, ?, ?)""",
            (
                agent["agent_id"],
                agent.get("specialization", ""),
                agent.get("memory_summary", ""),
                json.dumps(agent.get("active_objectives", [])),
                float(agent.get("workload_score", 0.0)),
            ),
        )
        self._conn.commit()

    def list_agents(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT agent_id, specialization, memory_summary, active_objectives, workload_score FROM persistent_agents").fetchall()
        return [
            {
                "agent_id": r[0],
                "specialization": r[1],
                "memory_summary": r[2],
                "active_objectives": json.loads(r[3] or "[]"),
                "workload_score": r[4],
            }
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()
''')

w("persistent_agents/persistent_agents_runtime.py", '''"""Persistent agents runtime (Prompt 52)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.persistent_agents.agent_store import AgentStore

DEFAULT_AGENTS = (
    ("architect", "Architect"),
    ("debugger", "Debugger"),
    ("researcher", "Researcher"),
    ("reviewer", "Reviewer"),
    ("optimizer", "Optimizer"),
    ("planner", "Planner"),
    ("documentation", "Documentation"),
    ("infrastructure", "Infrastructure"),
)


class PersistentAgentsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "persistent_agents.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = AgentStore(db)

    async def restore_agents(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "persistent_agents_enabled", False):
            return {"accepted": False, "reason": "persistent_agents_disabled"}
        existing = {a["agent_id"] for a in self._store.list_agents()}
        restored = 0
        for agent_id, spec in DEFAULT_AGENTS:
            if agent_id not in existing:
                self._store.upsert({
                    "agent_id": agent_id,
                    "specialization": spec,
                    "memory_summary": "",
                    "active_objectives": [],
                    "workload_score": 0.0,
                })
                restored += 1
        self._emit("persistent_agent_restored", {"restored": restored})
        return {"accepted": True, "agents": self._store.list_agents(), "supervised": True}

    async def assign_objective(self, *, agent_id: str, objective: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "persistent_agents_enabled", False):
            return {"accepted": False, "reason": "persistent_agents_disabled"}
        agents = {a["agent_id"]: a for a in self._store.list_agents()}
        agent = agents.get(agent_id)
        if not agent:
            return {"accepted": False, "reason": "agent_not_found"}
        objs = list(agent.get("active_objectives", []))
        objs.append(objective[:120])
        agent["active_objectives"] = objs[-8:]
        self._store.upsert(agent)
        self._emit("persistent_agent_assigned", {"agent_id": agent_id, "objective": objective[:80]})
        return {"accepted": True, "agent": agent, "approval_required": True}

    async def update_agent_state(self, *, agent_id: str, workload: float) -> dict[str, Any]:
        agents = {a["agent_id"]: a for a in self._store.list_agents()}
        agent = agents.get(agent_id)
        if not agent:
            return {"accepted": False, "reason": "agent_not_found"}
        agent["workload_score"] = min(1.0, max(0.0, workload))
        self._store.upsert(agent)
        return {"accepted": True, "agent": agent}

    async def compute_agent_load(self) -> dict[str, Any]:
        agents = self._store.list_agents()
        total = sum(a.get("workload_score", 0.0) for a in agents)
        return {"accepted": True, "total_load": total, "agent_count": len(agents)}

    async def summarize_agent_memory(self, *, agent_id: str) -> dict[str, Any]:
        agents = {a["agent_id"]: a for a in self._store.list_agents()}
        agent = agents.get(agent_id)
        if not agent:
            return {"accepted": False, "reason": "agent_not_found"}
        return {"accepted": True, "summary": agent.get("memory_summary", ""), "agent_id": agent_id}

    def snapshot(self) -> dict[str, Any]:
        return {"agents": len(self._store.list_agents())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="persistent_agents")
''')

w("persistent_agents/__init__.py", '''from odin_backend.core.persistent_agents.persistent_agents_runtime import PersistentAgentsRuntime

__all__ = ["PersistentAgentsRuntime"]
''')

# --- runtime_coordination ---
w("runtime_coordination/runtime_coordination_runtime.py", '''"""Runtime coordination (Prompt 52)."""
from __future__ import annotations
from typing import Any


class RuntimeCoordinationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def detect_runtime_overlap(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_coordination_enabled", False):
            return {"accepted": False, "reason": "runtime_coordination_disabled"}
        active = []
        for name in ("realtime_cognition", "autonomous_loop_v2", "cognitive_daemon_v2"):
            if hasattr(self._app, name):
                active.append(name)
        overlap = len(active) > 2
        if overlap:
            self._emit("runtime_overlap_detected", {"runtimes": active})
        return {"accepted": True, "active": active, "overlap": overlap}

    async def merge_contexts(self) -> dict[str, Any]:
        merged = {"runtimes": [], "supervised": True}
        if hasattr(self._app, "memory_intelligence"):
            merged["memory"] = True
        if hasattr(self._app, "workspace_coordination"):
            merged["workspace"] = True
        return {"accepted": True, "context": merged}

    async def resolve_priority_conflicts(self) -> dict[str, Any]:
        self._emit("runtime_conflict_resolved", {"resolved": True})
        return {"accepted": True, "resolved": True, "bounded": True}

    async def synchronize_streams(self) -> dict[str, Any]:
        return {"accepted": True, "synchronized": True, "prioritized": True}

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="runtime_coordination")
''')

w("runtime_coordination/__init__.py", '''from odin_backend.core.runtime_coordination.runtime_coordination_runtime import RuntimeCoordinationRuntime

__all__ = ["RuntimeCoordinationRuntime"]
''')

# --- cognitive_state ---
w("cognitive_state/cognitive_state_runtime.py", '''"""Cognitive state runtime (Prompt 52)."""
from __future__ import annotations
from typing import Any


class CognitiveStateRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "balanced"

    async def compute_cognitive_state(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_state_enabled", False):
            return {"accepted": False, "reason": "cognitive_state_disabled"}
        pressure = await self.estimate_runtime_pressure()
        engagement = await self.estimate_operator_load()
        state = {
            "mode": self._mode,
            "cognitive_pressure": pressure.get("pressure", 0.4),
            "operator_engagement": engagement.get("load", 0.5),
            "focus_depth": 0.6,
            "memory_saturation": 0.3,
        }
        self._emit("cognitive_state_updated", state)
        return {"accepted": True, "state": state}

    async def estimate_operator_load(self) -> dict[str, Any]:
        load = 0.5
        if hasattr(self._app, "operator_intelligence_v4"):
            r = await self._app.operator_intelligence_v4.predict(hours=4.0)
            if r.get("accepted"):
                load = r.get("load_forecast", {}).get("forecast_load", 0.5)
        return {"accepted": True, "load": load}

    async def estimate_runtime_pressure(self) -> dict[str, Any]:
        pressure = 0.4
        if hasattr(self._app, "cognitive_scheduler"):
            snap = self._app.cognitive_scheduler.snapshot()
            pressure = min(1.0, (snap.get("active", 0) + snap.get("deferred", 0)) / 32.0)
        return {"accepted": True, "pressure": pressure}

    async def export_state_snapshot(self) -> dict[str, Any]:
        return await self.compute_cognitive_state()

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_state")
''')

w("cognitive_state/__init__.py", '''from odin_backend.core.cognitive_state.cognitive_state_runtime import CognitiveStateRuntime

__all__ = ["CognitiveStateRuntime"]
''')

# --- unified_cognitive_core ---
w("unified_cognitive_core/unified_cognitive_core_runtime.py", '''"""Unified cognitive core orchestration (Prompt 52)."""
from __future__ import annotations
from typing import Any


class UnifiedCognitiveCoreRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._objectives: list[str] = []
        self._tick_count = 0

    async def cognition_tick(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "unified_cognitive_core_enabled", False):
            return {"accepted": False, "reason": "unified_cognitive_core_disabled"}
        self._emit("cognition_tick_started", {"tick": self._tick_count})
        if hasattr(self._app, "realtime_cognition"):
            await self._app.realtime_cognition.heartbeat()
        if hasattr(self._app, "attention_engine"):
            await self._app.attention_engine.calculate_attention_weights()
        if hasattr(self._app, "cognitive_state"):
            await self._app.cognitive_state.compute_cognitive_state()
        self._tick_count += 1
        self._emit("cognition_tick_completed", {"tick": self._tick_count})
        return {"accepted": True, "tick": self._tick_count, "no_direct_execution": True}

    async def synchronize_runtimes(self) -> dict[str, Any]:
        if hasattr(self._app, "runtime_coordination"):
            overlap = await self._app.runtime_coordination.detect_runtime_overlap()
            await self._app.runtime_coordination.synchronize_streams()
            return {"accepted": True, "sync": overlap}
        return {"accepted": True, "sync": {"runtimes": []}}

    async def rebuild_context(self) -> dict[str, Any]:
        if hasattr(self._app, "memory_intelligence"):
            await self._app.memory_intelligence.recall_contextual(query="global")
        self._emit("global_context_rebuilt", {"rebuilt": True})
        return {"accepted": True, "rebuilt": True}

    async def update_attention(self, *, focus: str) -> dict[str, Any]:
        if hasattr(self._app, "attention_engine"):
            return await self._app.attention_engine.shift_attention(focus=focus)
        return {"accepted": False, "reason": "attention_engine_unavailable"}

    async def checkpoint_global_state(self) -> dict[str, Any]:
        snap = {
            "objectives": list(self._objectives),
            "tick": self._tick_count,
        }
        if hasattr(self._app, "cognitive_state"):
            snap["cognitive_state"] = (await self._app.cognitive_state.export_state_snapshot()).get("state")
        return {"accepted": True, "checkpoint": snap}

    def snapshot(self) -> dict[str, Any]:
        profile = getattr(self._app.settings, "global_cognition_profile", "balanced")
        return {"tick_count": self._tick_count, "objectives": len(self._objectives), "profile": profile}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="unified_cognitive_core")
''')

w("unified_cognitive_core/__init__.py", '''from odin_backend.core.unified_cognitive_core.unified_cognitive_core_runtime import UnifiedCognitiveCoreRuntime

__all__ = ["UnifiedCognitiveCoreRuntime"]
''')

print("bootstrap_p52_core complete")

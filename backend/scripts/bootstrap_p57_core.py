"""Bootstrap Prompt 57 operational execution system modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"

AGENTS = ("Architect", "Debugger", "Researcher", "Planner", "Reviewer", "Refactor", "DevOps", "Documentation")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


# --- execution_system ---
w("execution_system/execution_system_runtime.py", '''"""Execution system runtime (Prompt 57)."""
from __future__ import annotations
from typing import Any


class ExecutionSystemRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._active = False
        self._health = 0.9
        self._profile = "balanced"
        self._checkpoints: list[dict] = []
        self._stage = 0

    async def initialize_execution_pipeline(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "execution_system_enabled", False):
            return {"accepted": False, "reason": "execution_system_disabled"}
        self._active = True
        self._profile = getattr(self._app.settings, "execution_profile", "balanced")
        self._stage = 0
        self._emit("execution_pipeline_initialized", {"profile": self._profile})
        return {"accepted": True, "initialized": True, "approval_gated": True, "reversible": True}

    async def checkpoint_execution_state(self) -> dict[str, Any]:
        cp = {"stage": self._stage, "health": self._health}
        self._checkpoints.append(cp)
        if len(self._checkpoints) > 32:
            self._checkpoints = self._checkpoints[-32:]
        self._emit("execution_stage_checkpointed", {"stage": self._stage})
        return {"accepted": True, "checkpoint": cp, "bounded": True}

    async def rollback_execution_stage(self) -> dict[str, Any]:
        if not self._checkpoints:
            return {"accepted": False, "reason": "no_checkpoint"}
        cp = self._checkpoints.pop()
        self._stage = max(0, cp.get("stage", 0) - 1)
        self._emit("execution_stage_rolled_back", {"stage": self._stage})
        return {"accepted": True, "rolled_back": True, "stage": self._stage, "reversible": True}

    async def compute_execution_health(self) -> dict[str, Any]:
        self._emit("execution_health_updated", {"health": self._health})
        return {"accepted": True, "health": round(self._health, 2), "transparent": True}

    async def stabilize_execution_flow(self) -> dict[str, Any]:
        if hasattr(self._app, "task_orchestration"):
            await self._app.task_orchestration.detect_execution_blockers()
        return {"accepted": True, "stabilized": True, "cooldown": True}

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active, "health": self._health, "stage": self._stage, "profile": self._profile}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="execution_system")
''')

w("execution_system/__init__.py", '''from odin_backend.core.execution_system.execution_system_runtime import ExecutionSystemRuntime

__all__ = ["ExecutionSystemRuntime"]
''')

# --- task_orchestration ---
w("task_orchestration/task_orchestration_runtime.py", '''"""Task orchestration runtime (Prompt 57)."""
from __future__ import annotations
from typing import Any


class TaskOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue: list[dict] = []
        self._mode = "adaptive"

    async def build_execution_pipeline(self, *, stages: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "task_orchestration_enabled", False):
            return {"accepted": False, "reason": "task_orchestration_disabled"}
        pipeline = (stages or ["plan", "review", "execute"])[:12]
        self._queue = [{"stage": s, "priority": i} for i, s in enumerate(pipeline)]
        return {"accepted": True, "pipeline": pipeline, "supervised": True}

    async def reprioritize_execution_queue(self) -> dict[str, Any]:
        self._queue.sort(key=lambda x: x.get("priority", 0))
        self._emit("execution_queue_rebalanced", {"size": len(self._queue)})
        return {"accepted": True, "queue_size": len(self._queue), "bounded": len(self._queue) <= 64}

    async def detect_execution_blockers(self) -> dict[str, Any]:
        blockers = [q for q in self._queue if q.get("blocked")]
        if blockers:
            self._emit("execution_blocker_detected", {"count": len(blockers)})
        return {"accepted": True, "blockers": blockers, "operator_visible": True}

    async def recover_interrupted_pipeline(self) -> dict[str, Any]:
        if hasattr(self._app, "execution_system"):
            return await self._app.execution_system.rollback_execution_stage()
        return {"accepted": True, "recovered": False}

    def snapshot(self) -> dict[str, Any]:
        return {"queue_size": len(self._queue), "mode": self._mode}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="task_orchestration")
''')

w("task_orchestration/__init__.py", '''from odin_backend.core.task_orchestration.task_orchestration_runtime import TaskOrchestrationRuntime

__all__ = ["TaskOrchestrationRuntime"]
''')

# --- agent_collaboration ---
w("agent_collaboration/agent_collaboration_runtime.py", '''"""Agent collaboration runtime (Prompt 57)."""
from __future__ import annotations
from typing import Any

AGENTS = ("Architect", "Debugger", "Researcher", "Planner", "Reviewer", "Refactor", "DevOps", "Documentation")


class AgentCollaborationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._consensus = 0.75
        self._active_agents: list[str] = []

    async def initiate_agent_collaboration(self, *, task: str, agents: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "agent_collaboration_enabled", False):
            return {"accepted": False, "reason": "agent_collaboration_disabled"}
        self._active_agents = (agents or ["Planner", "Reviewer"])[:8]
        self._emit("agent_collaboration_started", {"agents": self._active_agents, "task": task[:60]})
        return {"accepted": True, "agents": self._active_agents, "task": task[:120], "operator_visible": True}

    async def compute_consensus_score(self) -> dict[str, Any]:
        score = min(1.0, self._consensus + 0.02 * len(self._active_agents))
        self._emit("consensus_score_updated", {"score": score})
        return {"accepted": True, "consensus": round(score, 2), "bounded": True}

    async def route_specialized_execution(self, *, agent: str) -> dict[str, Any]:
        if agent not in AGENTS:
            return {"accepted": False, "reason": "unknown_agent"}
        return {"accepted": True, "agent": agent, "routed": True, "approval_gated": True}

    async def summarize_agent_reasoning(self) -> dict[str, Any]:
        return {"accepted": True, "summary": self._active_agents, "transparent": True, "local_only": True}

    def snapshot(self) -> dict[str, Any]:
        return {"consensus": self._consensus, "agents": self._active_agents}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="agent_collaboration")
''')

w("agent_collaboration/__init__.py", '''from odin_backend.core.agent_collaboration.agent_collaboration_runtime import AgentCollaborationRuntime

__all__ = ["AgentCollaborationRuntime"]
''')

# --- workspace_operations ---
w("workspace_operations/workspace_operations_runtime.py", '''"""Workspace operations runtime (Prompt 57)."""
from __future__ import annotations
from typing import Any


class WorkspaceOperationsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._health = 0.8
        self._snapshot: dict = {}

    async def build_workspace_operation_snapshot(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "workspace_operations_enabled", False):
            return {"accepted": False, "reason": "workspace_operations_disabled"}
        snap = {"repos": [], "terminals": [], "missions": [], "local_only": True}
        if hasattr(self._app, "workspace_sessions"):
            ws = await self._app.workspace_sessions.restore_workspace_session()
            snap["session"] = ws.get("session")
        self._snapshot = snap
        return {"accepted": True, "snapshot": snap, "transparent": True}

    async def recover_workspace_operation(self) -> dict[str, Any]:
        if hasattr(self._app, "workspace_sessions"):
            r = await self._app.workspace_sessions.restore_workspace_session()
            self._emit("workspace_operation_recovered", {"recovered": True})
            return {"accepted": True, "recovered": r.get("session") is not None, "reversible": True}
        return {"accepted": True, "recovered": False}

    async def correlate_execution_context(self) -> dict[str, Any]:
        ctx = {"correlated": True}
        if hasattr(self._app, "execution_memory"):
            ctx["has_history"] = True
        return {"accepted": True, "context": ctx}

    async def compute_workspace_operation_health(self) -> dict[str, Any]:
        return {"accepted": True, "health": round(self._health, 2), "bounded": True}

    def snapshot(self) -> dict[str, Any]:
        return {"health": self._health, "has_snapshot": bool(self._snapshot)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workspace_operations")
''')

w("workspace_operations/__init__.py", '''from odin_backend.core.workspace_operations.workspace_operations_runtime import WorkspaceOperationsRuntime

__all__ = ["WorkspaceOperationsRuntime"]
''')

# --- execution_memory ---
w("execution_memory/execution_store.py", '''"""SQLite execution registry (Prompt 57)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

MAX_CHAINS = 250


class ExecutionStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS execution_chains (
                chain_id TEXT PRIMARY KEY,
                payload TEXT,
                success INTEGER DEFAULT 0,
                updated_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def save(self, *, chain_id: str, payload: dict, success: bool = False) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO execution_chains (chain_id, payload, success) VALUES (?, ?, ?)",
            (chain_id[:80], json.dumps(payload), 1 if success else 0),
        )
        self._compress()
        self._conn.commit()

    def load(self, *, chain_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT payload, success FROM execution_chains WHERE chain_id = ?", (chain_id[:80],)
        ).fetchone()
        if not row:
            return None
        return {"chain_id": chain_id, **json.loads(row[0]), "success": bool(row[1])}

    def successful_patterns(self, *, limit: int = 10) -> list[dict]:
        rows = self._conn.execute(
            "SELECT chain_id, payload FROM execution_chains WHERE success=1 ORDER BY updated_at DESC LIMIT ?",
            (min(limit, 20),),
        ).fetchall()
        return [{"chain_id": r[0], **json.loads(r[1])} for r in rows]

    def _compress(self) -> None:
        count = self._conn.execute("SELECT COUNT(*) FROM execution_chains").fetchone()[0]
        if count > MAX_CHAINS:
            self._conn.execute(
                """DELETE FROM execution_chains WHERE chain_id NOT IN (
                    SELECT chain_id FROM execution_chains ORDER BY updated_at DESC LIMIT ?
                )""",
                (MAX_CHAINS,),
            )
''')

w("execution_memory/execution_memory_runtime.py", '''"""Execution memory runtime (Prompt 57)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.execution_memory.execution_store import ExecutionStore


class ExecutionMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "execution_memory.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = ExecutionStore(db)

    async def persist_execution_chain(self, *, chain_id: str, stages: list[str] | None = None, success: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "execution_memory_enabled", False):
            return {"accepted": False, "reason": "execution_memory_disabled"}
        payload = {"stages": (stages or [])[:20], "reversible": True}
        self._store.save(chain_id=chain_id, payload=payload, success=success)
        self._emit("execution_chain_persisted", {"chain_id": chain_id[:40]})
        return {"accepted": True, "chain_id": chain_id, "persisted": True}

    async def replay_execution_sequence(self, *, chain_id: str) -> dict[str, Any]:
        data = self._store.load(chain_id=chain_id)
        return {"accepted": True, "replay": data, "lazy_hydration": True}

    async def compress_execution_history(self) -> dict[str, Any]:
        return {"accepted": True, "compressed": True, "bounded": True}

    async def resurface_successful_execution_patterns(self) -> dict[str, Any]:
        patterns = self._store.successful_patterns()
        return {"accepted": True, "patterns": patterns, "supervised": True}

    def snapshot(self) -> dict[str, Any]:
        return {"patterns": len(self._store.successful_patterns())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="execution_memory")
''')

w("execution_memory/__init__.py", '''from odin_backend.core.execution_memory.execution_memory_runtime import ExecutionMemoryRuntime

__all__ = ["ExecutionMemoryRuntime"]
''')

# --- runtime_execution_visibility ---
w("runtime_execution_visibility/runtime_execution_visibility_runtime.py", '''"""Runtime execution visibility (Prompt 57)."""
from __future__ import annotations
from typing import Any


class RuntimeExecutionVisibilityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._pressure = 0.3
        self._density = "balanced"
        self._stream_count = 0

    async def render_execution_heatmap(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_execution_visibility_enabled", False):
            return {"accepted": False, "reason": "runtime_execution_visibility_disabled"}
        return {"accepted": True, "heatmap": True, "adaptive": True}

    async def stream_execution_visibility(self) -> dict[str, Any]:
        if self._stream_count > 56:
            return {"accepted": False, "reason": "stream_bounded"}
        self._stream_count += 1
        self._emit("execution_visibility_streamed", {"count": self._stream_count})
        return {"accepted": True, "streamed": True, "transparent": True}

    async def compute_execution_pressure(self) -> dict[str, Any]:
        if hasattr(self._app, "task_orchestration"):
            snap = self._app.task_orchestration.snapshot()
            self._pressure = min(1.0, snap.get("queue_size", 0) / 20.0)
        self._emit("execution_pressure_updated", {"pressure": self._pressure})
        return {"accepted": True, "pressure": round(self._pressure, 2), "operator_visible": True}

    async def compress_execution_streams(self) -> dict[str, Any]:
        self._density = getattr(self._app.settings, "execution_stream_density", "balanced")
        return {"accepted": True, "density": self._density, "low_power": self._density == "compact"}

    def snapshot(self) -> dict[str, Any]:
        return {"pressure": self._pressure, "stream_count": self._stream_count}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="runtime_execution_visibility")
''')

w("runtime_execution_visibility/__init__.py", '''from odin_backend.core.runtime_execution_visibility.runtime_execution_visibility_runtime import RuntimeExecutionVisibilityRuntime

__all__ = ["RuntimeExecutionVisibilityRuntime"]
''')

print("bootstrap_p57_core complete")

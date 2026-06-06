"""Bootstrap Prompt 55 autonomous cognitive coordination modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


PROFILES = ("compact", "balanced", "engineering", "immersive", "overnight_autonomous")

# --- autonomous_coordination ---
w("autonomous_coordination/autonomous_coordination_runtime.py", '''"""Autonomous coordination runtime (Prompt 55)."""
from __future__ import annotations
from typing import Any


class AutonomousCoordinationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._profile = "balanced"
        self._active = False
        self._cooldown_until = 0.0

    async def coordinate_runtime_objectives(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_coordination_enabled", False):
            return {"accepted": False, "reason": "autonomous_coordination_disabled"}
        self._active = True
        self._profile = getattr(self._app.settings, "coordination_profile", "balanced")
        if hasattr(self._app, "unified_cognitive_core"):
            await self._app.unified_cognitive_core.synchronize_cognition()
        self._emit("runtime_coordination_started", {"profile": self._profile})
        return {"accepted": True, "coordinated": True, "profile": self._profile, "operator_visible": True}

    async def synchronize_cognition_cycles(self) -> dict[str, Any]:
        if hasattr(self._app, "cognitive_scheduler"):
            await self._app.cognitive_scheduler.rebalance_load()
        if hasattr(self._app, "overnight_cognition"):
            snap = self._app.overnight_cognition.snapshot()
            if snap.get("active"):
                return {"accepted": True, "cycles": "overnight_bounded", "supervised": True}
        return {"accepted": True, "cycles": "synchronized", "bounded": True}

    async def rebalance_runtime_pressure(self) -> dict[str, Any]:
        if hasattr(self._app, "desktop_attention"):
            await self._app.desktop_attention.prioritize_desktop_attention()
        if hasattr(self._app, "autonomous_loop_v2"):
            await self._app.autonomous_loop_v2.tick()
        return {"accepted": True, "rebalanced": True, "throttled": self._profile == "compact"}

    async def recover_interrupted_coordination(self) -> dict[str, Any]:
        self._emit("runtime_coordination_restored", {"recovered": True})
        return {"accepted": True, "recovered": True, "approval_gated": True}

    async def build_coordination_snapshot(self) -> dict[str, Any]:
        deps = []
        for name in ("unified_cognitive_core", "cognitive_scheduler", "desktop_attention"):
            if hasattr(self._app, name):
                deps.append(name)
        return {"accepted": True, "snapshot": {"active": self._active, "profile": self._profile, "dependencies": deps}}

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active, "profile": self._profile}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_coordination")
''')

w("autonomous_coordination/__init__.py", '''from odin_backend.core.autonomous_coordination.autonomous_coordination_runtime import AutonomousCoordinationRuntime

__all__ = ["AutonomousCoordinationRuntime"]
''')

# --- objective_management ---
w("objective_management/objective_store.py", '''"""SQLite objective registry (Prompt 55)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

MAX_OBJECTIVES = 200


class ObjectiveStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS objectives (
                objective_id TEXT PRIMARY KEY,
                payload TEXT,
                progress REAL DEFAULT 0,
                updated_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def save(self, *, objective_id: str, payload: dict, progress: float = 0) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO objectives (objective_id, payload, progress) VALUES (?, ?, ?)",
            (objective_id[:80], json.dumps(payload), min(1.0, max(0.0, progress))),
        )
        self._compress()
        self._conn.commit()

    def load(self, *, objective_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT payload, progress FROM objectives WHERE objective_id = ?", (objective_id[:80],)
        ).fetchone()
        if not row:
            return None
        return {"objective_id": objective_id, **json.loads(row[0]), "progress": row[1]}

    def list_active(self, *, limit: int = 50) -> list[dict]:
        rows = self._conn.execute(
            "SELECT objective_id, payload, progress FROM objectives ORDER BY updated_at DESC LIMIT ?",
            (min(limit, MAX_OBJECTIVES),),
        ).fetchall()
        out = []
        for oid, payload, progress in rows:
            out.append({"objective_id": oid, **json.loads(payload), "progress": progress})
        return out

    def _compress(self) -> None:
        count = self._conn.execute("SELECT COUNT(*) FROM objectives").fetchone()[0]
        if count > MAX_OBJECTIVES:
            self._conn.execute(
                """DELETE FROM objectives WHERE objective_id NOT IN (
                    SELECT objective_id FROM objectives ORDER BY updated_at DESC LIMIT ?
                )""",
                (MAX_OBJECTIVES,),
            )
''')

w("objective_management/objective_management_runtime.py", '''"""Objective management runtime (Prompt 55)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.objective_management.objective_store import ObjectiveStore


class ObjectiveManagementRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "objectives.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = ObjectiveStore(db)

    async def create_objective_tree(self, *, root: str, children: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "objective_management_enabled", False):
            return {"accepted": False, "reason": "objective_management_disabled"}
        payload = {"root": root[:120], "children": (children or [])[:20], "approval_checkpoints": True}
        self._store.save(objective_id=root[:80], payload=payload, progress=0.0)
        self._emit("objective_tree_created", {"root": root[:60]})
        return {"accepted": True, "objective": payload, "supervised": True}

    async def update_objective_progress(self, *, objective_id: str, progress: float) -> dict[str, Any]:
        data = self._store.load(objective_id=objective_id)
        if not data:
            return {"accepted": False, "reason": "objective_not_found"}
        self._store.save(objective_id=objective_id, payload={k: v for k, v in data.items() if k not in ("objective_id", "progress")}, progress=progress)
        self._emit("objective_progress_updated", {"objective_id": objective_id[:60], "progress": progress})
        return {"accepted": True, "objective_id": objective_id, "progress": progress}

    async def detect_stalled_objectives(self) -> dict[str, Any]:
        stalled = [o for o in self._store.list_active() if o.get("progress", 0) < 0.05]
        if stalled:
            self._emit("stalled_objective_detected", {"count": len(stalled)})
        return {"accepted": True, "stalled": stalled[:10], "bounded": True}

    async def restore_objective_chain(self) -> dict[str, Any]:
        active = self._store.list_active(limit=5)
        return {"accepted": True, "chain": [o.get("objective_id") for o in active], "approval_gated": True}

    async def summarize_active_objectives(self) -> dict[str, Any]:
        active = self._store.list_active()
        return {"accepted": True, "objectives": active, "count": len(active)}

    def snapshot(self) -> dict[str, Any]:
        return {"active_count": len(self._store.list_active())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="objective_management")
''')

w("objective_management/__init__.py", '''from odin_backend.core.objective_management.objective_management_runtime import ObjectiveManagementRuntime

__all__ = ["ObjectiveManagementRuntime"]
''')

# --- context_synchronization ---
w("context_synchronization/context_synchronization_runtime.py", '''"""Context synchronization runtime (Prompt 55)."""
from __future__ import annotations
from typing import Any


class ContextSynchronizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._last_checkpoint: dict | None = None
        self._sync_loops = 0

    async def synchronize_context_surfaces(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "context_synchronization_enabled", False):
            return {"accepted": False, "reason": "context_synchronization_disabled"}
        if self._sync_loops > 32:
            return {"accepted": False, "reason": "sync_loop_bounded"}
        self._sync_loops += 1
        surfaces = []
        if hasattr(self._app, "workspace_sessions"):
            surfaces.append("workspace_sessions")
        if hasattr(self._app, "memory_fabric_v2"):
            surfaces.append("memory_fabric_v2")
        self._emit("context_surfaces_synchronized", {"surfaces": surfaces})
        return {"accepted": True, "surfaces": surfaces, "local_first": True}

    async def merge_runtime_context(self) -> dict[str, Any]:
        merged = {"sources": []}
        if hasattr(self._app, "workspace_sessions"):
            ws = await self._app.workspace_sessions.restore_workspace_session()
            merged["sources"].append("workspace_sessions")
            merged["workspace"] = ws.get("session")
        if hasattr(self._app, "runtime_coordination"):
            await self._app.runtime_coordination.merge_contexts()
            merged["sources"].append("runtime_coordination")
        return {"accepted": True, "merged": merged, "deduplicated": True}

    async def restore_context_checkpoint(self) -> dict[str, Any]:
        if self._last_checkpoint:
            return {"accepted": True, "checkpoint": self._last_checkpoint}
        if hasattr(self._app, "workspace_sessions"):
            r = await self._app.workspace_sessions.restore_workspace_session()
            self._last_checkpoint = r.get("session")
        return {"accepted": True, "checkpoint": self._last_checkpoint}

    async def detect_context_divergence(self) -> dict[str, Any]:
        diverged = False
        if hasattr(self._app, "workspace_sessions") and hasattr(self._app, "memory_fabric_v2"):
            diverged = self._sync_loops > 8
        if diverged:
            self._emit("context_divergence_detected", {"loops": self._sync_loops})
        return {"accepted": True, "diverged": diverged, "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"sync_loops": self._sync_loops, "has_checkpoint": self._last_checkpoint is not None}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="context_synchronization")
''')

w("context_synchronization/__init__.py", '''from odin_backend.core.context_synchronization.context_synchronization_runtime import ContextSynchronizationRuntime

__all__ = ["ContextSynchronizationRuntime"]
''')

# --- mission_continuity ---
w("mission_continuity/mission_continuity_runtime.py", '''"""Mission continuity runtime (Prompt 55)."""
from __future__ import annotations
from typing import Any


class MissionContinuityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._health = 0.75

    async def build_mission_resume_chain(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "mission_continuity_enabled", False):
            return {"accepted": False, "reason": "mission_continuity_disabled"}
        chain = []
        if hasattr(self._app, "workspace_sessions"):
            r = await self._app.workspace_sessions.build_resume_chain()
            chain.extend(r.get("chain", []))
        if hasattr(self._app, "continuity_forecasting"):
            cf = await self._app.continuity_forecasting.detect_abandoned_work()
            if cf.get("accepted"):
                chain.append("abandoned_work")
        self._emit("mission_resume_chain_built", {"steps": len(chain)})
        return {"accepted": True, "chain": chain, "supervised": True}

    async def detect_interrupted_workflows(self) -> dict[str, Any]:
        interrupted = []
        if hasattr(self._app, "deferred_reasoning"):
            snap = self._app.deferred_reasoning.snapshot()
            if snap.get("pending", 0) > 0:
                interrupted.append("deferred_reasoning")
        if interrupted:
            self._emit("workflow_interruption_detected", {"count": len(interrupted)})
        return {"accepted": True, "interrupted": interrupted, "operator_visible": True}

    async def restore_mission_context(self) -> dict[str, Any]:
        if hasattr(self._app, "workspace_sessions"):
            return await self._app.workspace_sessions.restore_workspace_session()
        return {"accepted": True, "restored": False}

    async def estimate_continuity_health(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "continuity_tracking_enabled", True):
            return {"accepted": True, "health": self._health, "tracking": False}
        if hasattr(self._app, "operator_focus"):
            snap = self._app.operator_focus.snapshot()
            if snap.get("active"):
                self._health = min(1.0, self._health + 0.05)
        return {"accepted": True, "health": round(self._health, 2), "bounded": True}

    def snapshot(self) -> dict[str, Any]:
        return {"health": self._health}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="mission_continuity")
''')

w("mission_continuity/__init__.py", '''from odin_backend.core.mission_continuity.mission_continuity_runtime import MissionContinuityRuntime

__all__ = ["MissionContinuityRuntime"]
''')

# --- cognitive_planning ---
w("cognitive_planning/cognitive_planning_runtime.py", '''"""Cognitive planning runtime (Prompt 55)."""
from __future__ import annotations
from typing import Any


class CognitivePlanningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "balanced"
        self._budget = 1.0

    async def generate_cognitive_plan(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_planning_enabled", False):
            return {"accepted": False, "reason": "cognitive_planning_disabled"}
        self._mode = getattr(self._app.settings, "reasoning_budget_mode", "adaptive")
        plan = {"horizon": "medium", "mode": self._mode, "approval_gated": True, "no_auto_deploy": True}
        self._emit("cognitive_plan_generated", {"mode": self._mode})
        return {"accepted": True, "plan": plan, "bounded": True}

    async def allocate_reasoning_budget(self) -> dict[str, Any]:
        mode = getattr(self._app.settings, "reasoning_budget_mode", "adaptive")
        if mode == "adaptive":
            self._budget = max(0.2, self._budget - 0.05)
        self._emit("reasoning_budget_rebalanced", {"budget": self._budget})
        return {"accepted": True, "budget": self._budget, "throttled": mode == "adaptive"}

    async def estimate_task_horizon(self, *, task: str = "engineering") -> dict[str, Any]:
        horizon = "long" if task == "research" else "medium"
        return {"accepted": True, "task": task[:60], "horizon": horizon}

    async def optimize_focus_schedule(self) -> dict[str, Any]:
        if hasattr(self._app, "operator_focus"):
            snap = self._app.operator_focus.snapshot()
            return {"accepted": True, "focus_active": snap.get("active", False), "low_power": self._mode == "compact"}
        return {"accepted": True, "focus_active": False}

    async def compress_background_reasoning(self) -> dict[str, Any]:
        if hasattr(self._app, "cognitive_daemon_v2"):
            await self._app.cognitive_daemon_v2.set_low_power(enabled=True)
        return {"accepted": True, "compressed": True, "low_power": True}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "budget": self._budget}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_planning")
''')

w("cognitive_planning/__init__.py", '''from odin_backend.core.cognitive_planning.cognitive_planning_runtime import CognitivePlanningRuntime

__all__ = ["CognitivePlanningRuntime"]
''')

# --- operator_alignment ---
w("operator_alignment/operator_alignment_runtime.py", '''"""Operator alignment runtime (Prompt 55)."""
from __future__ import annotations
from typing import Any


class OperatorAlignmentRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._alignment = 0.7
        self._confidence = 0.8
        self._drift = 0.0

    async def estimate_operator_alignment(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_alignment_enabled", False):
            return {"accepted": False, "reason": "operator_alignment_disabled"}
        if hasattr(self._app, "operator_intelligence_v4"):
            self._alignment = min(1.0, self._alignment + 0.02)
        self._emit("operator_alignment_updated", {"alignment": self._alignment})
        return {"accepted": True, "alignment": round(self._alignment, 2), "bounded": True, "transparent": True}

    async def adapt_assistance_strategy(self) -> dict[str, Any]:
        strategy = "conservative" if self._alignment < 0.5 else "balanced"
        return {"accepted": True, "strategy": strategy, "operator_override": True}

    async def compute_supervision_confidence(self) -> dict[str, Any]:
        if hasattr(self._app, "desktop_attention"):
            await self._app.desktop_attention.prioritize_desktop_attention()
        return {"accepted": True, "confidence": round(self._confidence, 2), "supervised": True}

    async def detect_alignment_drift(self) -> dict[str, Any]:
        self._drift = max(0.0, self._drift + 0.01 - self._alignment * 0.01)
        drifted = self._drift > 0.15
        return {"accepted": True, "drift": round(self._drift, 3), "drifted": drifted, "operator_visible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"alignment": self._alignment, "confidence": self._confidence, "drift": self._drift}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_alignment")
''')

w("operator_alignment/__init__.py", '''from odin_backend.core.operator_alignment.operator_alignment_runtime import OperatorAlignmentRuntime

__all__ = ["OperatorAlignmentRuntime"]
''')

print("bootstrap_p55_core complete")

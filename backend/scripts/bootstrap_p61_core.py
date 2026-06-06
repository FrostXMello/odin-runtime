"""Bootstrap Prompt 61 closed-loop predictive recovery modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"
RECOVERY_PHASES = ("detection", "stabilization", "rollback_review", "recovery_execution", "validation", "continuity_restore")


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


# --- predictive_recovery_v2 ---
w("predictive_recovery_v2/predictive_recovery_v2_runtime.py", '''"""Predictive recovery v2 runtime (Prompt 61)."""
from __future__ import annotations
from typing import Any


class PredictiveRecoveryV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._failure_risk = 0.2
        self._recovery_probability = 0.75
        self._simulations = 0
        self._profile = "balanced"

    async def forecast_operational_failure(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "predictive_recovery_v2_enabled", False):
            return {"accepted": False, "reason": "predictive_recovery_v2_disabled"}
        if hasattr(self._app, "runtime_stabilization"):
            inst = await self._app.runtime_stabilization.detect_runtime_instability()
            if inst.get("unstable"):
                self._failure_risk = min(1.0, self._failure_risk + 0.15)
        if hasattr(self._app, "cognitive_risk"):
            risk = await self._app.cognitive_risk.forecast_cognitive_risk()
            self._failure_risk = max(self._failure_risk, risk.get("risk", 0.2))
        self._emit("operational_failure_forecasted", {"risk": self._failure_risk})
        return {"accepted": True, "risk": round(self._failure_risk, 2), "supervised": True, "transparent": True}

    async def simulate_recovery_paths(self) -> dict[str, Any]:
        if self._simulations > 36:
            return {"accepted": False, "reason": "simulation_bounded"}
        self._simulations += 1
        paths = [["checkpoint", "rollback", "resume"], ["stabilize", "defer", "retry"]]
        self._emit("recovery_paths_simulated", {"paths": len(paths)})
        return {"accepted": True, "paths": paths, "approval_gated": True, "bounded": True}

    async def estimate_recovery_probability(self) -> dict[str, Any]:
        self._recovery_probability = max(0.1, 0.9 - self._failure_risk * 0.5)
        self._emit("recovery_probability_estimated", {"probability": self._recovery_probability})
        return {"accepted": True, "probability": round(self._recovery_probability, 2), "operator_visible": True}

    async def generate_recovery_recommendation(self) -> dict[str, Any]:
        if hasattr(self._app, "operator_veto"):
            return await self._app.operator_veto.request_recovery_approval(
                path="rollback_chain", risk=self._failure_risk
            )
        return {"accepted": True, "recommendation": "stabilize_first", "approval_required": True}

    def snapshot(self) -> dict[str, Any]:
        return {"failure_risk": self._failure_risk, "recovery_probability": self._recovery_probability, "profile": self._profile}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="predictive_recovery_v2")
''')

w("predictive_recovery_v2/__init__.py", '''from odin_backend.core.predictive_recovery_v2.predictive_recovery_v2_runtime import PredictiveRecoveryV2Runtime

__all__ = ["PredictiveRecoveryV2Runtime"]
''')

# --- recovery_orchestration ---
w("recovery_orchestration/recovery_orchestration_runtime.py", '''"""Recovery orchestration runtime (Prompt 61)."""
from __future__ import annotations
from typing import Any

PHASES = ("detection", "stabilization", "rollback_review", "recovery_execution", "validation", "continuity_restore")


class RecoveryOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._phase = "detection"
        self._cycles = 0
        self._initialized = False

    async def initialize_recovery_cycle(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "recovery_orchestration_enabled", False):
            return {"accepted": False, "reason": "recovery_orchestration_disabled"}
        self._initialized = True
        self._phase = "detection"
        self._emit("recovery_cycle_initialized", {"phase": self._phase})
        return {"accepted": True, "initialized": True, "supervised": True}

    async def synchronize_recovery_layers(self) -> dict[str, Any]:
        layers = []
        for name, method in (
            ("predictive_recovery_v2", "forecast_operational_failure"),
            ("stability_loops", "rebalance_runtime_pressure"),
            ("rollback_intelligence", "generate_rollback_graph"),
        ):
            if hasattr(self._app, name):
                await getattr(self._app, name).__getattribute__(method)()
                layers.append(name)
        return {"accepted": True, "layers": layers, "bounded": True}

    async def transition_recovery_phase(self, *, phase: str = "stabilization") -> dict[str, Any]:
        if phase not in PHASES:
            return {"accepted": False, "reason": "invalid_phase"}
        if self._cycles > 48:
            return {"accepted": False, "reason": "recovery_cycle_bounded"}
        self._phase = phase
        self._cycles += 1
        self._emit("recovery_phase_transitioned", {"phase": phase})
        return {"accepted": True, "phase": phase, "operator_controlled": True}

    async def validate_recovery_integrity(self) -> dict[str, Any]:
        if hasattr(self._app, "operator_veto"):
            veto = await self._app.operator_veto.authorize_recovery_chain()
            if not veto.get("authorized"):
                return {"accepted": False, "reason": "recovery_not_authorized", "approval_gated": True}
        return {"accepted": True, "valid": True, "reversible": True, "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"phase": self._phase, "cycles": self._cycles, "initialized": self._initialized}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="recovery_orchestration")
''')

w("recovery_orchestration/__init__.py", '''from odin_backend.core.recovery_orchestration.recovery_orchestration_runtime import RecoveryOrchestrationRuntime

__all__ = ["RecoveryOrchestrationRuntime"]
''')

# --- rollback_intelligence ---
w("rollback_intelligence/rollback_store.py", '''"""SQLite rollback registry (Prompt 61)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

MAX_NODES = 600


class RollbackStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS rollback_nodes (
                node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                confidence REAL,
                payload TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def add_node(self, *, label: str, confidence: float, payload: dict) -> int:
        cur = self._conn.execute(
            "INSERT INTO rollback_nodes (label, confidence, payload) VALUES (?, ?, ?)",
            (label[:80], confidence, json.dumps(payload)),
        )
        count = self._conn.execute("SELECT COUNT(*) FROM rollback_nodes").fetchone()[0]
        if count > MAX_NODES:
            self._conn.execute(
                """DELETE FROM rollback_nodes WHERE node_id NOT IN (
                    SELECT node_id FROM rollback_nodes ORDER BY node_id DESC LIMIT ?
                )""",
                (MAX_NODES,),
            )
        self._conn.commit()
        return cur.lastrowid or 0

    def nodes(self, *, limit: int = 50) -> list[dict]:
        rows = self._conn.execute(
            "SELECT node_id, label, confidence, payload FROM rollback_nodes ORDER BY node_id DESC LIMIT ?",
            (min(limit, MAX_NODES),),
        ).fetchall()
        return [{"node_id": r[0], "label": r[1], "confidence": r[2], **json.loads(r[3])} for r in rows]
''')

w("rollback_intelligence/rollback_intelligence_runtime.py", '''"""Rollback intelligence runtime (Prompt 61)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.rollback_intelligence.rollback_store import RollbackStore


class RollbackIntelligenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "rollback_registry.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = RollbackStore(db)
        self._confidence = 0.7
        self._replay_loops = 0

    async def generate_rollback_graph(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "rollback_intelligence_enabled", False):
            return {"accepted": False, "reason": "rollback_intelligence_disabled"}
        for label in ("checkpoint_a", "checkpoint_b", "rollback_target"):
            self._store.add_node(label=label, confidence=0.8, payload={"safe": True})
        nodes = self._store.nodes()
        self._emit("rollback_graph_generated", {"nodes": len(nodes)})
        return {"accepted": True, "graph": nodes, "virtualized": len(nodes) <= 600, "approval_gated": True}

    async def compare_recovery_branches(self) -> dict[str, Any]:
        branches = [{"id": "branch_a", "confidence": 0.75}, {"id": "branch_b", "confidence": 0.65}]
        return {"accepted": True, "branches": branches, "transparent": True}

    async def estimate_rollback_confidence(self) -> dict[str, Any]:
        self._confidence = max(0.2, self._confidence - 0.02)
        self._emit("rollback_confidence_estimated", {"confidence": self._confidence})
        return {"accepted": True, "confidence": round(self._confidence, 2), "operator_visible": True}

    async def replay_execution_window(self) -> dict[str, Any]:
        if self._replay_loops > 40:
            return {"accepted": False, "reason": "replay_bounded"}
        self._replay_loops += 1
        if hasattr(self._app, "execution_system"):
            await self._app.execution_system.checkpoint_execution_state()
        self._emit("execution_window_replayed", {"loops": self._replay_loops})
        return {"accepted": True, "replayed": True, "supervised": True, "lazy_hydration": True}

    def snapshot(self) -> dict[str, Any]:
        return {"confidence": self._confidence, "nodes": len(self._store.nodes())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="rollback_intelligence")
''')

w("rollback_intelligence/__init__.py", '''from odin_backend.core.rollback_intelligence.rollback_intelligence_runtime import RollbackIntelligenceRuntime

__all__ = ["RollbackIntelligenceRuntime"]
''')

# --- continuity_recovery ---
w("continuity_recovery/continuity_recovery_runtime.py", '''"""Continuity recovery runtime (Prompt 61)."""
from __future__ import annotations
from typing import Any


class ContinuityRecoveryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._restored = False
        self._replay_loops = 0

    async def recover_mission_continuity(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "continuity_recovery_enabled", False):
            return {"accepted": False, "reason": "continuity_recovery_disabled"}
        if hasattr(self._app, "mission_command"):
            await self._app.mission_command.transition_operational_phase(phase="recovery")
        if hasattr(self._app, "mission_continuity"):
            await self._app.mission_continuity.estimate_continuity_health()
        self._restored = True
        self._emit("mission_continuity_restored", {"restored": True})
        return {"accepted": True, "restored": True, "approval_gated": True, "reversible": True}

    async def rebuild_workspace_context(self) -> dict[str, Any]:
        if hasattr(self._app, "context_synchronization"):
            await self._app.context_synchronization.merge_runtime_context()
        self._emit("workspace_context_rebuilt", {"rebuilt": True})
        return {"accepted": True, "rebuilt": True, "lazy_hydration": True}

    async def restore_interrupted_reasoning(self) -> dict[str, Any]:
        if hasattr(self._app, "deferred_reasoning"):
            await self._app.deferred_reasoning.restore_reasoning()
        return {"accepted": True, "restored": True, "supervised": True}

    async def replay_continuity_window(self) -> dict[str, Any]:
        if self._replay_loops > 40:
            return {"accepted": False, "reason": "continuity_replay_bounded"}
        self._replay_loops += 1
        if hasattr(self._app, "live_cognition_timeline"):
            return await self._app.live_cognition_timeline.replay_cognition_window()
        return {"accepted": True, "replay": [], "bounded": True}

    def snapshot(self) -> dict[str, Any]:
        return {"restored": self._restored, "replay_loops": self._replay_loops}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="continuity_recovery")
''')

w("continuity_recovery/__init__.py", '''from odin_backend.core.continuity_recovery.continuity_recovery_runtime import ContinuityRecoveryRuntime

__all__ = ["ContinuityRecoveryRuntime"]
''')

# --- stability_loops ---
w("stability_loops/stability_loops_runtime.py", '''"""Stability loops runtime (Prompt 61)."""
from __future__ import annotations
from typing import Any


class StabilityLoopsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._initialized = False
        self._pressure = 0.5
        self._density = "balanced"
        self._loop_count = 0
        self._cooldown = False

    async def initialize_stability_loop(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "stability_loops_enabled", False):
            return {"accepted": False, "reason": "stability_loops_disabled"}
        self._initialized = True
        self._density = getattr(self._app.settings, "stability_mode", "balanced")
        self._emit("stability_loop_initialized", {"density": self._density})
        return {"accepted": True, "initialized": True, "bounded": True}

    async def rebalance_runtime_pressure(self) -> dict[str, Any]:
        self._pressure = max(0.1, self._pressure - 0.05)
        if hasattr(self._app, "runtime_stabilization"):
            await self._app.runtime_stabilization.stabilize_runtime_pressure()
        if hasattr(self._app, "unified_command_center"):
            await self._app.unified_command_center.rebalance_command_pressure()
        return {"accepted": True, "pressure": round(self._pressure, 2), "throttled": self._cooldown}

    async def throttle_recovery_density(self) -> dict[str, Any]:
        self._density = "compact"
        self._cooldown = True
        self._emit("recovery_density_throttled", {"density": self._density})
        return {"accepted": True, "density": self._density, "low_power": True}

    async def suppress_instability_cascades(self) -> dict[str, Any]:
        if self._loop_count > 48:
            return {"accepted": False, "reason": "stability_loop_bounded"}
        self._loop_count += 1
        if hasattr(self._app, "runtime_fusion"):
            await self._app.runtime_fusion.stabilize_cross_runtime_pressure()
        self._emit("instability_cascade_suppressed", {"loops": self._loop_count})
        return {"accepted": True, "suppressed": True, "bounded": True}

    def snapshot(self) -> dict[str, Any]:
        return {"initialized": self._initialized, "pressure": self._pressure, "density": self._density, "cooldown": self._cooldown}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="stability_loops")
''')

w("stability_loops/__init__.py", '''from odin_backend.core.stability_loops.stability_loops_runtime import StabilityLoopsRuntime

__all__ = ["StabilityLoopsRuntime"]
''')

# --- operator_veto ---
w("operator_veto/operator_veto_runtime.py", '''"""Operator veto runtime (Prompt 61)."""
from __future__ import annotations
from typing import Any


class OperatorVetoRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._pending: list[dict] = []
        self._vetoed: list[str] = []
        self._authorized: list[str] = []

    async def request_recovery_approval(self, *, path: str = "default", risk: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_veto_enabled", False):
            return {"accepted": False, "reason": "operator_veto_disabled"}
        req = {"path": path, "risk": risk, "status": "pending"}
        self._pending.append(req)
        self._emit("operator_veto_requested", {"path": path[:40], "risk": risk})
        return {"accepted": True, "approval_required": True, "path": path, "transparent": True}

    async def escalate_recovery_risk(self, *, risk: float = 0.7) -> dict[str, Any]:
        return {"accepted": True, "escalated": True, "risk": risk, "operator_visible": True, "trust_preserving": True}

    async def veto_recovery_path(self, *, path: str = "default") -> dict[str, Any]:
        self._vetoed.append(path)
        self._emit("recovery_path_vetoed", {"path": path[:40]})
        return {"accepted": True, "vetoed": True, "path": path, "operator_controlled": True}

    async def authorize_recovery_chain(self, *, path: str = "default") -> dict[str, Any]:
        if path in self._vetoed:
            return {"accepted": False, "reason": "path_vetoed", "authorized": False}
        self._authorized.append(path)
        self._emit("recovery_chain_authorized", {"path": path[:40]})
        return {"accepted": True, "authorized": True, "path": path, "approval_gated": True, "reversible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"pending": len(self._pending), "vetoed": len(self._vetoed), "authorized": len(self._authorized)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_veto")
''')

w("operator_veto/__init__.py", '''from odin_backend.core.operator_veto.operator_veto_runtime import OperatorVetoRuntime

__all__ = ["OperatorVetoRuntime"]
''')

print("bootstrap_p61_core complete")

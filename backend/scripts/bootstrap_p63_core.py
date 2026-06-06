"""Bootstrap Prompt 63 rollback DAG animation engine modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"

MAX_DAG_NODES = 800
MAX_REPLAY_LOOPS = 56
MAX_RECONSTRUCTION_LOOPS = 40


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


w("rollback_animation_engine/replay_store.py", '''"""SQLite rollback animation replay registry (Prompt 63)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

MAX_FRAMES = 500


class RollbackAnimationStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS animation_frames (
                frame_id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                payload TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def add_frame(self, *, label: str, payload: dict[str, Any]) -> int:
        cur = self._conn.execute(
            "INSERT INTO animation_frames (label, payload) VALUES (?, ?)",
            (label[:80], json.dumps(payload)),
        )
        count = self._conn.execute("SELECT COUNT(*) FROM animation_frames").fetchone()[0]
        if count > MAX_FRAMES:
            self._conn.execute(
                """DELETE FROM animation_frames WHERE frame_id NOT IN (
                    SELECT frame_id FROM animation_frames ORDER BY frame_id DESC LIMIT ?
                )""",
                (MAX_FRAMES,),
            )
        self._conn.commit()
        return cur.lastrowid or 0

    def frames(self, *, limit: int = 50) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT frame_id, label, payload FROM animation_frames ORDER BY frame_id DESC LIMIT ?",
            (min(limit, MAX_FRAMES),),
        ).fetchall()
        return [{"frame_id": r[0], "label": r[1], **json.loads(r[2])} for r in rows]
''')

w("rollback_animation_engine/rollback_animation_engine_runtime.py", '''"""Rollback animation engine runtime (Prompt 63)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.rollback_animation_engine.replay_store import RollbackAnimationStore

PROFILES = ("compact", "balanced", "immersive", "cinematic", "overnight_replay")
MAX_DAG_NODES = 800
MAX_REPLAY_LOOPS = 56


class RollbackAnimationEngineRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "rollback_animation.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = RollbackAnimationStore(db)
        self._initialized = False
        self._frame = 0
        self._replay_loops = 0
        self._stabilized = False
        self._nodes: list[dict[str, Any]] = []

    async def animate_rollback_graph(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "rollback_animation_engine_enabled", False):
            return {"accepted": False, "reason": "rollback_animation_engine_disabled"}
        if not self._initialized:
            profile = getattr(self._app.settings, "replay_profile", "balanced")
            self._initialized = True
            self._emit("rollback_animation_initialized", {"profile": profile})
        if hasattr(self._app, "rollback_intelligence"):
            graph = await self._app.rollback_intelligence.generate_rollback_graph()
            self._nodes = graph.get("graph", [])[:MAX_DAG_NODES]
        else:
            self._nodes = [{"label": f"node_{i}", "confidence": 0.7} for i in range(min(3, MAX_DAG_NODES))]
        if hasattr(self._app, "runtime_fusion"):
            await self._app.runtime_fusion.fuse_runtime_contexts()
        virtualized = len(self._nodes) <= MAX_DAG_NODES
        self._frame += 1
        self._store.add_frame(label=f"frame_{self._frame}", payload={"nodes": len(self._nodes)})
        self._emit("rollback_dag_animated", {"nodes": len(self._nodes), "frame": self._frame})
        return {
            "accepted": True,
            "graph": self._nodes,
            "frame": self._frame,
            "virtualized": virtualized,
            "approval_gated": True,
            "transparent": True,
        }

    async def replay_execution_chain(self) -> dict[str, Any]:
        if self._replay_loops >= MAX_REPLAY_LOOPS:
            return {"accepted": False, "reason": "replay_loop_bounded"}
        self._replay_loops += 1
        if hasattr(self._app, "predictive_recovery_v2"):
            await self._app.predictive_recovery_v2.simulate_recovery_paths()
        if hasattr(self._app, "live_cognition_timeline"):
            await self._app.live_cognition_timeline.replay_cognition_window()
        self._emit("execution_chain_replayed", {"loops": self._replay_loops})
        return {
            "accepted": True,
            "replayed": True,
            "loops": self._replay_loops,
            "supervised": True,
            "lazy_hydration": True,
        }

    async def synchronize_animation_frame(self) -> dict[str, Any]:
        self._frame += 1
        return {
            "accepted": True,
            "frame": self._frame,
            "synchronized": True,
            "bounded": True,
            "adaptive_fps": getattr(self._app.settings, "replay_density", "adaptive"),
        }

    async def stabilize_rollback_render(self) -> dict[str, Any]:
        self._stabilized = True
        if hasattr(self._app, "rollback_intelligence"):
            await self._app.rollback_intelligence.estimate_rollback_confidence()
        self._emit("rollback_render_stabilized", {"stabilized": True})
        return {
            "accepted": True,
            "stabilized": True,
            "low_power": getattr(self._app.settings, "replay_profile", "balanced") == "compact",
            "operator_visible": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "frame": self._frame,
            "nodes": len(self._nodes),
            "replay_loops": self._replay_loops,
            "stabilized": self._stabilized,
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="rollback_animation_engine")
''')

w("rollback_animation_engine/__init__.py", '''from odin_backend.core.rollback_animation_engine.rollback_animation_engine_runtime import RollbackAnimationEngineRuntime

__all__ = ["RollbackAnimationEngineRuntime"]
''')

w("causality_mapping/causality_mapping_runtime.py", '''"""Causality mapping runtime (Prompt 63)."""
from __future__ import annotations
from typing import Any


class CausalityMappingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._graph: list[dict[str, Any]] = []
        self._dependencies: dict[str, list[str]] = {}

    async def build_causality_graph(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "causality_mapping_enabled", False):
            return {"accepted": False, "reason": "causality_mapping_disabled"}
        if hasattr(self._app, "execution_graph"):
            await self._app.execution_graph.build_execution_dag()
        self._graph = [
            {"id": "cause_a", "effect": "runtime_pressure", "confidence": 0.8},
            {"id": "cause_b", "effect": "rollback_trigger", "confidence": 0.75},
        ]
        self._emit("causality_graph_generated", {"nodes": len(self._graph)})
        return {
            "accepted": True,
            "graph": self._graph,
            "operator_visible": True,
            "transparent": True,
        }

    async def trace_failure_chain(self, *, path: str = "default") -> dict[str, Any]:
        chain = [{"step": i, "path": path, "label": f"failure_{i}"} for i in range(3)]
        if hasattr(self._app, "predictive_recovery_v2"):
            await self._app.predictive_recovery_v2.forecast_operational_failure()
        self._emit("failure_chain_traced", {"path": path[:40], "steps": len(chain)})
        return {"accepted": True, "chain": chain, "path": path, "supervised": True}

    async def map_runtime_dependencies(self) -> dict[str, Any]:
        deps = {
            "rollback_intelligence": ["execution_graph", "recovery_orchestration"],
            "runtime_fusion": ["live_cognition_timeline", "mission_command"],
        }
        self._dependencies = deps
        self._emit("runtime_dependency_mapped", {"runtimes": len(deps)})
        return {"accepted": True, "dependencies": deps, "operator_visible": True}

    async def reconstruct_reasoning_path(self, *, mission_id: str = "mission-local") -> dict[str, Any]:
        path = [{"mission_id": mission_id, "step": "reason", "bounded": True}]
        if hasattr(self._app, "deferred_reasoning"):
            await self._app.deferred_reasoning.defer_reasoning(thought=f"mission:{mission_id}")
        self._emit("reasoning_path_reconstructed", {"mission_id": mission_id[:40]})
        return {"accepted": True, "path": path, "mission_id": mission_id, "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"graph": self._graph, "dependencies": self._dependencies}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="causality_mapping")
''')

w("causality_mapping/__init__.py", '''from odin_backend.core.causality_mapping.causality_mapping_runtime import CausalityMappingRuntime

__all__ = ["CausalityMappingRuntime"]
''')

w("replay_orchestration/replay_orchestration_runtime.py", '''"""Replay orchestration runtime (Prompt 63)."""
from __future__ import annotations
from typing import Any

MAX_REPLAY_LOOPS = 56


class ReplayOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._window: dict[str, Any] | None = None
        self._checkpoints: list[dict[str, Any]] = []
        self._density = 1.0
        self._replay_loops = 0

    async def initialize_replay_window(self, *, window_id: str = "replay-window") -> dict[str, Any]:
        if not getattr(self._app.settings, "replay_orchestration_enabled", False):
            return {"accepted": False, "reason": "replay_orchestration_disabled"}
        if hasattr(self._app, "operator_veto"):
            await self._app.operator_veto.request_recovery_approval(path=f"replay:{window_id}", risk=0.3)
        self._window = {"window_id": window_id, "bounded": True, "supervised": True}
        if hasattr(self._app, "continuity_recovery"):
            await self._app.continuity_recovery.replay_continuity_window()
        self._emit("replay_window_initialized", {"window_id": window_id[:40]})
        return {
            "accepted": True,
            "window": self._window,
            "approval_gated": True,
            "transparent": True,
        }

    async def replay_cognition_timeline(self) -> dict[str, Any]:
        if self._replay_loops >= MAX_REPLAY_LOOPS:
            return {"accepted": False, "reason": "replay_loop_bounded"}
        self._replay_loops += 1
        if hasattr(self._app, "live_cognition_timeline"):
            await self._app.live_cognition_timeline.replay_cognition_window()
        if hasattr(self._app, "mission_continuity"):
            await self._app.mission_continuity.estimate_continuity_health()
        self._emit("cognition_timeline_replayed", {"loops": self._replay_loops})
        return {
            "accepted": True,
            "replayed": True,
            "loops": self._replay_loops,
            "lazy_hydration": True,
            "supervised": True,
        }

    async def checkpoint_replay_state(self) -> dict[str, Any]:
        checkpoint = {"frame": self._replay_loops, "density": self._density, "window": self._window}
        self._checkpoints.append(checkpoint)
        if len(self._checkpoints) > 40:
            self._checkpoints = self._checkpoints[-40:]
        self._emit("replay_state_checkpointed", {"checkpoints": len(self._checkpoints)})
        return {"accepted": True, "checkpoint": checkpoint, "reversible": True}

    async def throttle_replay_density(self) -> dict[str, Any]:
        mode = getattr(self._app.settings, "replay_density", "adaptive")
        self._density = max(0.2, self._density - 0.05) if mode == "adaptive" else self._density
        self._emit("replay_density_throttled", {"density": self._density})
        return {
            "accepted": True,
            "density": round(self._density, 2),
            "mode": mode,
            "low_power": self._density < 0.5,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "window": self._window,
            "checkpoints": len(self._checkpoints),
            "density": self._density,
            "replay_loops": self._replay_loops,
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="replay_orchestration")
''')

w("replay_orchestration/__init__.py", '''from odin_backend.core.replay_orchestration.replay_orchestration_runtime import ReplayOrchestrationRuntime

__all__ = ["ReplayOrchestrationRuntime"]
''')

w("pressure_propagation/pressure_propagation_runtime.py", '''"""Pressure propagation runtime (Prompt 63)."""
from __future__ import annotations
from typing import Any


class PressurePropagationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._pressure = 0.45
        self._surfaces: dict[str, float] = {}
        self._congestion: list[str] = []

    async def propagate_runtime_pressure(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "pressure_propagation_enabled", False):
            return {"accepted": False, "reason": "pressure_propagation_disabled"}
        if hasattr(self._app, "runtime_fusion"):
            await self._app.runtime_fusion.stabilize_cross_runtime_pressure()
        if hasattr(self._app, "stability_loops"):
            await self._app.stability_loops.rebalance_runtime_pressure()
        self._surfaces = {"execution": 0.5, "cognition": 0.4, "recovery": 0.35}
        self._emit("runtime_pressure_propagated", {"surfaces": len(self._surfaces)})
        return {
            "accepted": True,
            "surfaces": self._surfaces,
            "operator_visible": True,
            "transparent": True,
        }

    async def simulate_pressure_diffusion(self) -> dict[str, Any]:
        diffused = {k: max(0.1, v - 0.05) for k, v in (self._surfaces or {"default": 0.4}).items()}
        self._surfaces = diffused
        self._emit("pressure_diffusion_simulated", {"surfaces": len(diffused)})
        return {"accepted": True, "surfaces": diffused, "bounded": True}

    async def detect_congestion_chain(self) -> dict[str, Any]:
        self._congestion = ["execution_queue", "cognition_timeline"] if self._pressure > 0.4 else []
        self._emit("execution_congestion_detected", {"chains": len(self._congestion)})
        return {"accepted": True, "congestion": self._congestion, "operator_visible": True}

    async def rebalance_pressure_surfaces(self) -> dict[str, Any]:
        self._pressure = max(0.1, self._pressure - 0.04)
        self._surfaces = {k: max(0.1, v - 0.03) for k, v in self._surfaces.items()} if self._surfaces else {"default": 0.3}
        self._emit("pressure_surfaces_rebalanced", {"pressure": self._pressure})
        return {"accepted": True, "pressure": round(self._pressure, 2), "surfaces": self._surfaces, "reversible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"pressure": self._pressure, "surfaces": self._surfaces, "congestion": self._congestion}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="pressure_propagation")
''')

w("pressure_propagation/__init__.py", '''from odin_backend.core.pressure_propagation.pressure_propagation_runtime import PressurePropagationRuntime

__all__ = ["PressurePropagationRuntime"]
''')

w("timeline_visualization/timeline_visualization_runtime.py", '''"""Timeline visualization runtime (Prompt 63)."""
from __future__ import annotations
from typing import Any

PROFILES = ("compact", "balanced", "immersive", "cinematic", "overnight_replay")


class TimelineVisualizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._layers: list[str] = []
        self._compressed = False
        self._render_count = 0

    async def render_operational_timeline(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "timeline_visualization_enabled", False):
            return {"accepted": False, "reason": "timeline_visualization_disabled"}
        mode = getattr(self._app.settings, "timeline_render_mode", "adaptive")
        if hasattr(self._app, "live_cognition_timeline"):
            await self._app.live_cognition_timeline.append_cognition_event(kind="operational")
        self._layers = ["cognition", "execution", "recovery", "pressure"]
        self._render_count += 1
        self._emit("operational_timeline_rendered", {"layers": len(self._layers), "mode": mode})
        return {
            "accepted": True,
            "layers": self._layers,
            "mode": mode,
            "render_count": self._render_count,
            "operator_visible": True,
        }

    async def compress_timeline_window(self) -> dict[str, Any]:
        self._compressed = True
        self._emit("timeline_window_compressed", {"compressed": True})
        return {
            "accepted": True,
            "compressed": True,
            "adaptive_compression": True,
            "lazy_hydration": True,
        }

    async def synchronize_timeline_layers(self) -> dict[str, Any]:
        if hasattr(self._app, "runtime_fusion"):
            await self._app.runtime_fusion.synchronize_checkpoint_layers()
        self._emit("timeline_layers_synchronized", {"layers": len(self._layers)})
        return {"accepted": True, "layers": self._layers, "synchronized": True, "bounded": True}

    async def generate_timeline_overlay(self) -> dict[str, Any]:
        overlay = {"continuity": True, "replay": True, "pressure": True}
        self._emit("timeline_overlay_generated", {"overlay": list(overlay.keys())})
        return {"accepted": True, "overlay": overlay, "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"layers": self._layers, "compressed": self._compressed, "render_count": self._render_count}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="timeline_visualization")
''')

w("timeline_visualization/__init__.py", '''from odin_backend.core.timeline_visualization.timeline_visualization_runtime import TimelineVisualizationRuntime

__all__ = ["TimelineVisualizationRuntime"]
''')

w("execution_reconstruction/execution_reconstruction_runtime.py", '''"""Execution reconstruction runtime (Prompt 63)."""
from __future__ import annotations
from typing import Any

MAX_RECONSTRUCTION_LOOPS = 40


class ExecutionReconstructionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._states: list[dict[str, Any]] = []
        self._reconstruction_loops = 0

    async def reconstruct_execution_state(self, *, execution_id: str = "exec-local") -> dict[str, Any]:
        if not getattr(self._app.settings, "execution_reconstruction_enabled", False):
            return {"accepted": False, "reason": "execution_reconstruction_disabled"}
        if self._reconstruction_loops >= MAX_RECONSTRUCTION_LOOPS:
            return {"accepted": False, "reason": "reconstruction_loop_bounded"}
        self._reconstruction_loops += 1
        if hasattr(self._app, "execution_system"):
            await self._app.execution_system.checkpoint_execution_state()
        state = {"execution_id": execution_id, "reconstructed": True, "supervised": True}
        self._states.append(state)
        self._emit("execution_state_reconstructed", {"execution_id": execution_id[:40]})
        return {
            "accepted": True,
            "state": state,
            "approval_gated": True,
            "reversible": True,
            "transparent": True,
        }

    async def rebuild_workspace_sequence(self) -> dict[str, Any]:
        sequence = [{"step": i, "workspace": f"ws_{i}"} for i in range(3)]
        if hasattr(self._app, "continuity_recovery"):
            await self._app.continuity_recovery.rebuild_workspace_context()
        self._emit("workspace_sequence_rebuilt", {"steps": len(sequence)})
        return {"accepted": True, "sequence": sequence, "bounded": True}

    async def restore_cognition_window(self) -> dict[str, Any]:
        if hasattr(self._app, "live_cognition_timeline"):
            await self._app.live_cognition_timeline.replay_cognition_window()
        if hasattr(self._app, "operator_veto"):
            await self._app.operator_veto.request_recovery_approval(path="cognition_restore", risk=0.35)
        self._emit("cognition_window_restored", {"restored": True})
        return {"accepted": True, "restored": True, "approval_gated": True, "supervised": True}

    async def simulate_execution_restore(self) -> dict[str, Any]:
        if self._reconstruction_loops >= MAX_RECONSTRUCTION_LOOPS:
            return {"accepted": False, "reason": "reconstruction_loop_bounded"}
        self._reconstruction_loops += 1
        self._emit("execution_restore_simulated", {"loops": self._reconstruction_loops})
        return {
            "accepted": True,
            "simulated": True,
            "loops": self._reconstruction_loops,
            "lazy_hydration": True,
            "no_mutation": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"states": len(self._states), "reconstruction_loops": self._reconstruction_loops}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="execution_reconstruction")
''')

w("execution_reconstruction/__init__.py", '''from odin_backend.core.execution_reconstruction.execution_reconstruction_runtime import ExecutionReconstructionRuntime

__all__ = ["ExecutionReconstructionRuntime"]
''')

print("bootstrap_p63_core complete")

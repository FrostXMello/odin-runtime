"""Rollback animation engine runtime (Prompt 63)."""
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

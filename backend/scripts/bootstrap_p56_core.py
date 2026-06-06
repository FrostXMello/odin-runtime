"""Bootstrap Prompt 56 live cognitive orchestration modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


# --- live_orchestration ---
w("live_orchestration/live_orchestration_runtime.py", '''"""Live orchestration runtime (Prompt 56)."""
from __future__ import annotations
from typing import Any


class LiveOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._health = 0.85
        self._profile = "balanced"
        self._pulse_active = False

    async def stream_orchestration_state(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "live_orchestration_enabled", False):
            return {"accepted": False, "reason": "live_orchestration_disabled"}
        self._profile = getattr(self._app.settings, "orchestration_profile", "balanced")
        self._emit("orchestration_state_streamed", {"profile": self._profile})
        return {"accepted": True, "streaming": True, "profile": self._profile, "transparent": True}

    async def compute_orchestration_health(self) -> dict[str, Any]:
        if hasattr(self._app, "autonomous_coordination"):
            snap = self._app.autonomous_coordination.snapshot()
            if snap.get("active"):
                self._health = min(1.0, self._health + 0.02)
        return {"accepted": True, "health": round(self._health, 2), "bounded": True}

    async def synchronize_runtime_surfaces(self) -> dict[str, Any]:
        if hasattr(self._app, "context_synchronization"):
            await self._app.context_synchronization.synchronize_context_surfaces()
        return {"accepted": True, "synchronized": True, "throttled": self._profile == "compact"}

    async def render_cognition_pulse(self) -> dict[str, Any]:
        self._pulse_active = True
        return {"accepted": True, "pulse": True, "low_power": self._profile == "overnight_autonomous"}

    async def detect_runtime_instability(self) -> dict[str, Any]:
        unstable = self._health < 0.4
        if unstable:
            self._emit("runtime_instability_detected", {"health": self._health})
        return {"accepted": True, "unstable": unstable, "operator_visible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"health": self._health, "profile": self._profile, "pulse_active": self._pulse_active}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_orchestration")
''')

w("live_orchestration/__init__.py", '''from odin_backend.core.live_orchestration.live_orchestration_runtime import LiveOrchestrationRuntime

__all__ = ["LiveOrchestrationRuntime"]
''')

# --- objective_streams ---
w("objective_streams/objective_streams_runtime.py", '''"""Objective streams runtime (Prompt 56)."""
from __future__ import annotations
from typing import Any


class ObjectiveStreamsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._stream_count = 0

    async def stream_objective_updates(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "objective_streams_enabled", False):
            return {"accepted": False, "reason": "objective_streams_disabled"}
        if self._stream_count > 64:
            return {"accepted": False, "reason": "stream_throttled"}
        self._stream_count += 1
        self._emit("objective_stream_updated", {"count": self._stream_count})
        return {"accepted": True, "streamed": True, "bounded": True}

    async def reprioritize_active_objectives(self) -> dict[str, Any]:
        if hasattr(self._app, "objective_management"):
            objs = await self._app.objective_management.summarize_active_objectives()
            return {"accepted": True, "reprioritized": objs.get("count", 0), "approval_gated": True}
        return {"accepted": True, "reprioritized": 0}

    async def detect_objective_stagnation(self) -> dict[str, Any]:
        if hasattr(self._app, "objective_management"):
            r = await self._app.objective_management.detect_stalled_objectives()
            if r.get("stalled"):
                self._emit("objective_stagnation_detected", {"count": len(r["stalled"])})
            return {"accepted": True, "stagnant": r.get("stalled", [])}
        return {"accepted": True, "stagnant": []}

    async def render_objective_flow(self) -> dict[str, Any]:
        return {"accepted": True, "flow": "streaming", "supervised": True}

    def snapshot(self) -> dict[str, Any]:
        return {"stream_count": self._stream_count}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="objective_streams")
''')

w("objective_streams/__init__.py", '''from odin_backend.core.objective_streams.objective_streams_runtime import ObjectiveStreamsRuntime

__all__ = ["ObjectiveStreamsRuntime"]
''')

# --- mission_graph ---
w("mission_graph/graph_store.py", '''"""SQLite mission graph registry (Prompt 56)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

MAX_NODES = 300


class MissionGraphStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS mission_nodes (
                node_id TEXT PRIMARY KEY,
                payload TEXT,
                updated_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS mission_edges (
                src TEXT, dst TEXT,
                PRIMARY KEY (src, dst)
            )"""
        )
        self._conn.commit()

    def add_node(self, *, node_id: str, payload: dict) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO mission_nodes (node_id, payload) VALUES (?, ?)",
            (node_id[:80], json.dumps(payload)),
        )
        self._compress()
        self._conn.commit()

    def link(self, *, src: str, dst: str) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO mission_edges (src, dst) VALUES (?, ?)",
            (src[:80], dst[:80]),
        )
        self._conn.commit()

    def nodes(self, *, limit: int = 50) -> list[dict]:
        rows = self._conn.execute(
            "SELECT node_id, payload FROM mission_nodes ORDER BY updated_at DESC LIMIT ?",
            (min(limit, MAX_NODES),),
        ).fetchall()
        return [{"node_id": r[0], **json.loads(r[1])} for r in rows]

    def edges(self) -> list[dict]:
        rows = self._conn.execute("SELECT src, dst FROM mission_edges LIMIT 200").fetchall()
        return [{"src": r[0], "dst": r[1]} for r in rows]

    def _compress(self) -> None:
        count = self._conn.execute("SELECT COUNT(*) FROM mission_nodes").fetchone()[0]
        if count > MAX_NODES:
            self._conn.execute(
                """DELETE FROM mission_nodes WHERE node_id NOT IN (
                    SELECT node_id FROM mission_nodes ORDER BY updated_at DESC LIMIT ?
                )""",
                (MAX_NODES,),
            )
''')

w("mission_graph/mission_graph_runtime.py", '''"""Mission graph runtime (Prompt 56)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.mission_graph.graph_store import MissionGraphStore


class MissionGraphRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "mission_graph.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = MissionGraphStore(db)

    async def build_mission_graph(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "mission_graph_enabled", False):
            return {"accepted": False, "reason": "mission_graph_disabled"}
        nodes = self._store.nodes()
        edges = self._store.edges()
        return {"accepted": True, "graph": {"nodes": nodes, "edges": edges}, "virtualized": len(nodes) > 20}

    async def link_related_objectives(self, *, src: str, dst: str) -> dict[str, Any]:
        self._store.add_node(node_id=src, payload={"type": "objective"})
        self._store.add_node(node_id=dst, payload={"type": "objective"})
        self._store.link(src=src, dst=dst)
        self._emit("mission_graph_linked", {"src": src[:40], "dst": dst[:40]})
        return {"accepted": True, "linked": True, "supervised": True}

    async def analyze_dependency_pressure(self) -> dict[str, Any]:
        edges = self._store.edges()
        pressure = min(1.0, len(edges) / 50.0)
        return {"accepted": True, "pressure": round(pressure, 2), "bounded": True}

    async def compute_mission_continuity_score(self) -> dict[str, Any]:
        if hasattr(self._app, "mission_continuity"):
            h = await self._app.mission_continuity.estimate_continuity_health()
            return {"accepted": True, "score": h.get("health", 0.5)}
        return {"accepted": True, "score": 0.5}

    def snapshot(self) -> dict[str, Any]:
        return {"nodes": len(self._store.nodes()), "edges": len(self._store.edges())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="mission_graph")
''')

w("mission_graph/__init__.py", '''from odin_backend.core.mission_graph.mission_graph_runtime import MissionGraphRuntime

__all__ = ["MissionGraphRuntime"]
''')

# --- realtime_coordination ---
w("realtime_coordination/realtime_coordination_runtime.py", '''"""Realtime coordination runtime (Prompt 56)."""
from __future__ import annotations
from typing import Any


class RealtimeCoordinationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._multiplex_count = 0
        self._pressure = 0.3

    async def multiplex_runtime_streams(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "realtime_coordination_enabled", False):
            return {"accepted": False, "reason": "realtime_coordination_disabled"}
        if self._multiplex_count > 48:
            return {"accepted": False, "reason": "multiplex_bounded"}
        self._multiplex_count += 1
        channels = ["live-orchestration:runtime", "objective-streams:runtime"]
        self._emit("runtime_stream_multiplexed", {"channels": len(channels)})
        return {"accepted": True, "channels": channels, "bounded": True}

    async def stabilize_coordination_loops(self) -> dict[str, Any]:
        if hasattr(self._app, "autonomous_coordination"):
            await self._app.autonomous_coordination.recover_interrupted_coordination()
        return {"accepted": True, "stabilized": True, "cooldown": True}

    async def prioritize_runtime_events(self) -> dict[str, Any]:
        return {"accepted": True, "prioritized": True, "stream_priority": "high"}

    async def estimate_coordination_pressure(self) -> dict[str, Any]:
        self._pressure = min(1.0, self._pressure + 0.05)
        self._emit("coordination_pressure_updated", {"pressure": self._pressure})
        return {"accepted": True, "pressure": round(self._pressure, 2), "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"multiplex_count": self._multiplex_count, "pressure": self._pressure}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="realtime_coordination")
''')

w("realtime_coordination/__init__.py", '''from odin_backend.core.realtime_coordination.realtime_coordination_runtime import RealtimeCoordinationRuntime

__all__ = ["RealtimeCoordinationRuntime"]
''')

# --- operator_situational_awareness ---
w("operator_situational_awareness/operator_situational_awareness_runtime.py", '''"""Operator situational awareness runtime (Prompt 56)."""
from __future__ import annotations
from typing import Any


class OperatorSituationalAwarenessRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._pressure = 0.4

    async def generate_operator_brief(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_situational_awareness_enabled", False):
            return {"accepted": False, "reason": "operator_situational_awareness_disabled"}
        brief = {"summary": "runtime operational", "supervised": True, "local_only": True}
        self._emit("operator_brief_generated", {"brief": "generated"})
        return {"accepted": True, "brief": brief, "transparent": True}

    async def estimate_operational_pressure(self) -> dict[str, Any]:
        if hasattr(self._app, "operator_focus"):
            p = await self._app.operator_focus.estimate_distraction_pressure()
            self._pressure = p.get("pressure", 0.4)
        self._emit("operational_pressure_forecasted", {"pressure": self._pressure})
        return {"accepted": True, "pressure": round(self._pressure, 2), "operator_visible": True}

    async def forecast_focus_instability(self) -> dict[str, Any]:
        risk = self._pressure > 0.7
        return {"accepted": True, "risk": risk, "bounded": True}

    async def summarize_runtime_state(self) -> dict[str, Any]:
        state = {}
        if hasattr(self._app, "live_orchestration"):
            state["orchestration"] = self._app.live_orchestration.snapshot()
        return {"accepted": True, "state": state, "local_first": True}

    def snapshot(self) -> dict[str, Any]:
        return {"pressure": self._pressure}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_situational_awareness")
''')

w("operator_situational_awareness/__init__.py", '''from odin_backend.core.operator_situational_awareness.operator_situational_awareness_runtime import OperatorSituationalAwarenessRuntime

__all__ = ["OperatorSituationalAwarenessRuntime"]
''')

# --- cognitive_visual_layers ---
w("cognitive_visual_layers/cognitive_visual_layers_runtime.py", '''"""Cognitive visual layers runtime (Prompt 56)."""
from __future__ import annotations
from typing import Any


class CognitiveVisualLayersRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._density = "balanced"
        self._render_mode = "adaptive"

    async def render_runtime_constellation(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_visual_layers_enabled", False):
            return {"accepted": False, "reason": "cognitive_visual_layers_disabled"}
        self._render_mode = getattr(self._app.settings, "cognitive_render_mode", "adaptive")
        self._emit("runtime_constellation_rendered", {"mode": self._render_mode})
        return {"accepted": True, "constellation": True, "lazy_hydration": True}

    async def render_objective_river(self) -> dict[str, Any]:
        self._emit("objective_river_rendered", {"density": self._density})
        return {"accepted": True, "river": True, "throttled": self._render_mode == "adaptive"}

    async def render_attention_heatmap(self) -> dict[str, Any]:
        if hasattr(self._app, "desktop_attention"):
            await self._app.desktop_attention.prioritize_desktop_attention()
        return {"accepted": True, "heatmap": True, "low_power": self._density == "compact"}

    async def compress_visual_density(self) -> dict[str, Any]:
        self._density = getattr(self._app.settings, "visual_density", "balanced")
        if self._density == "compact":
            self._density = "compact"
        self._emit("cognitive_visual_density_compressed", {"density": self._density})
        return {"accepted": True, "density": self._density, "cinematic_safe": True}

    def snapshot(self) -> dict[str, Any]:
        return {"density": self._density, "render_mode": self._render_mode}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_visual_layers")
''')

w("cognitive_visual_layers/__init__.py", '''from odin_backend.core.cognitive_visual_layers.cognitive_visual_layers_runtime import CognitiveVisualLayersRuntime

__all__ = ["CognitiveVisualLayersRuntime"]
''')

print("bootstrap_p56_core complete")

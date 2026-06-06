"""Bootstrap Prompt 54 native autonomous desktop modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


PROFILES = ("compact", "balanced", "immersive", "engineering", "overnight", "cinematic")

# --- native_desktop ---
w("native_desktop/native_desktop_runtime.py", '''"""Native desktop runtime (Prompt 54)."""
from __future__ import annotations
from typing import Any


class NativeDesktopRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._initialized = False
        self._profile = "balanced"
        self._low_power = False

    async def initialize_desktop_runtime(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_desktop_enabled", False):
            return {"accepted": False, "reason": "native_desktop_disabled"}
        self._initialized = True
        self._profile = getattr(self._app.settings, "desktop_profile", "balanced")
        if hasattr(self._app, "native_os"):
            await self._app.native_os.show_tray()
        self._emit("desktop_runtime_initialized", {"profile": self._profile})
        return {"accepted": True, "initialized": True, "profile": self._profile, "transparent": True}

    async def register_tray_actions(self) -> dict[str, Any]:
        return {"accepted": True, "actions": ["focus", "briefing", "pause"], "operator_controlled": True}

    async def dispatch_native_notification(self, *, title: str, body: str = "") -> dict[str, Any]:
        if hasattr(self._app, "native_os"):
            r = await self._app.native_os.notify(title=title, body=body)
            self._emit("native_notification_dispatched", {"title": title[:60]})
            return r
        return {"accepted": True, "dispatched": True}

    async def restore_desktop_session(self) -> dict[str, Any]:
        if hasattr(self._app, "workspace_sessions"):
            return await self._app.workspace_sessions.restore_workspace_session()
        return {"accepted": True, "restored": False}

    async def enter_low_power_mode(self, *, enabled: bool = True) -> dict[str, Any]:
        self._low_power = enabled
        if hasattr(self._app, "cognitive_daemon_v2"):
            await self._app.cognitive_daemon_v2.set_low_power(enabled=enabled)
        return {"accepted": True, "low_power": enabled}

    def snapshot(self) -> dict[str, Any]:
        return {"initialized": self._initialized, "profile": self._profile, "low_power": self._low_power}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="native_desktop")
''')

w("native_desktop/__init__.py", '''from odin_backend.core.native_desktop.native_desktop_runtime import NativeDesktopRuntime

__all__ = ["NativeDesktopRuntime"]
''')

# --- window_awareness ---
w("window_awareness/window_classifier.py", '''from __future__ import annotations


def classify(*, title: str, app: str = "") -> dict:
    kind = "editor"
    t = title.lower()
    if "terminal" in t or app.lower() in ("powershell", "cmd", "iterm"):
        kind = "terminal"
    elif "chrome" in app.lower() or "browser" in t:
        kind = "browser"
    return {"kind": kind, "title": title[:120], "local_only": True}
''')

w("window_awareness/window_awareness_runtime.py", '''"""Window awareness runtime (Prompt 54)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.window_awareness.window_classifier import classify


class WindowAwarenessRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._active = {"title": "Odin", "app": "odin"}
        self._exclusions: list[str] = []
        self._monitoring_visible = True

    async def detect_workspace_transition(self, *, window: str, app: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "window_awareness_enabled", False):
            return {"accepted": False, "reason": "window_awareness_disabled"}
        if not getattr(self._app.settings, "window_tracking_enabled", True):
            return {"accepted": False, "reason": "window_tracking_disabled"}
        prior = self._active.copy()
        self._active = {"title": window[:120], "app": app[:60]}
        if prior.get("title") != window:
            self._emit("workspace_transition_detected", {"from": prior.get("title"), "to": window[:60]})
        return {"accepted": True, "transition": True, "transparent": True, "exclusions": self._exclusions}

    async def classify_active_window(self) -> dict[str, Any]:
        c = classify(title=self._active.get("title", ""), app=self._active.get("app", ""))
        self._emit("active_window_classified", c)
        return {"accepted": True, "classification": c}

    async def estimate_focus_depth(self) -> dict[str, Any]:
        depth = 0.7 if self._active.get("app") not in self._exclusions else 0.2
        return {"accepted": True, "depth": depth}

    async def build_workspace_snapshot(self) -> dict[str, Any]:
        c = classify(title=self._active.get("title", ""), app=self._active.get("app", ""))
        return {"accepted": True, "snapshot": {"active": self._active, "classification": c, "monitoring_visible": self._monitoring_visible}}

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active, "monitoring_visible": self._monitoring_visible}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="window_awareness")
''')

w("window_awareness/__init__.py", '''from odin_backend.core.window_awareness.window_awareness_runtime import WindowAwarenessRuntime

__all__ = ["WindowAwarenessRuntime"]
''')

# --- live_overlays_v2 ---
w("live_overlays_v2/live_overlays_v2_runtime.py", '''"""Live overlays V2 (Prompt 54)."""
from __future__ import annotations
from typing import Any


class LiveOverlaysV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._attached: dict[str, bool] = {}
        self._suppressed: set[str] = set()
        self._mode = "adaptive"

    async def attach_overlay(self, *, overlay_type: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "live_overlays_v2_enabled", False):
            return {"accepted": False, "reason": "live_overlays_v2_disabled"}
        if overlay_type in self._suppressed:
            return {"accepted": False, "reason": "overlay_suppressed"}
        self._attached[overlay_type] = True
        self._emit("overlay_context_updated", {"overlay": overlay_type[:40]})
        return {"accepted": True, "overlay": overlay_type, "throttled": self._mode == "adaptive"}

    async def suppress_overlay(self, *, overlay_type: str) -> dict[str, Any]:
        self._suppressed.add(overlay_type[:40])
        self._attached.pop(overlay_type, None)
        self._emit("overlay_suppressed", {"overlay": overlay_type[:40]})
        return {"accepted": True, "suppressed": overlay_type}

    async def update_overlay_context(self, *, context: str) -> dict[str, Any]:
        self._emit("overlay_context_updated", {"context": context[:80]})
        return {"accepted": True, "context": context[:80]}

    async def render_focus_overlay(self) -> dict[str, Any]:
        if "focus_timer" in self._suppressed:
            return {"accepted": False, "reason": "suppressed"}
        return await self.attach_overlay(overlay_type="focus_timer")

    def snapshot(self) -> dict[str, Any]:
        return {"attached": list(self._attached.keys()), "suppressed": list(self._suppressed)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_overlays_v2")
''')

w("live_overlays_v2/__init__.py", '''from odin_backend.core.live_overlays_v2.live_overlays_v2_runtime import LiveOverlaysV2Runtime

__all__ = ["LiveOverlaysV2Runtime"]
''')

# --- workspace_sessions ---
w("workspace_sessions/session_store.py", '''"""SQLite workspace session registry (Prompt 54)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any


class WorkspaceSessionStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS workspace_sessions (
                session_id TEXT PRIMARY KEY,
                payload TEXT,
                updated_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def save(self, *, session_id: str, payload: dict) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO workspace_sessions (session_id, payload) VALUES (?, ?)",
            (session_id[:80], json.dumps(payload)),
        )
        self._conn.commit()

    def load(self, *, session_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT payload FROM workspace_sessions WHERE session_id = ?", (session_id[:80],)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def latest(self) -> dict | None:
        row = self._conn.execute(
            "SELECT session_id, payload FROM workspace_sessions ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        return {"session_id": row[0], **json.loads(row[1])}
''')

w("workspace_sessions/workspace_sessions_runtime.py", '''"""Workspace sessions runtime (Prompt 54)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.workspace_sessions.session_store import WorkspaceSessionStore


class WorkspaceSessionsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "workspace_sessions.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = WorkspaceSessionStore(db)

    async def save_workspace_session(self, *, session_id: str = "default", repo: str = "", files: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "workspace_sessions_enabled", False):
            return {"accepted": False, "reason": "workspace_sessions_disabled"}
        payload = {"repo": repo[:80], "files": (files or [])[:20], "supervised": True}
        self._store.save(session_id=session_id, payload=payload)
        self._emit("workspace_session_saved", {"session_id": session_id})
        return {"accepted": True, "session_id": session_id, "payload": payload}

    async def restore_workspace_session(self, *, session_id: str = "default") -> dict[str, Any]:
        if not getattr(self._app.settings, "workspace_sessions_enabled", False):
            return {"accepted": False, "reason": "workspace_sessions_disabled"}
        data = self._store.load(session_id=session_id) or self._store.latest()
        if data:
            self._emit("workspace_session_restored", {"session_id": session_id})
        return {"accepted": True, "session": data}

    async def merge_workspace_context(self) -> dict[str, Any]:
        if hasattr(self._app, "workspace_coordination"):
            return await self._app.workspace_coordination.coordinate(projects=["local"])
        return {"accepted": True, "merged": True}

    async def build_resume_chain(self) -> dict[str, Any]:
        session = await self.restore_workspace_session()
        chain = []
        if session.get("session"):
            chain.append("workspace")
        if hasattr(self._app, "deferred_reasoning"):
            dr = self._app.deferred_reasoning.snapshot()
            if dr.get("pending", 0) > 0:
                chain.append("deferred_reasoning")
        return {"accepted": True, "chain": chain}

    def snapshot(self) -> dict[str, Any]:
        latest = self._store.latest()
        return {"has_session": latest is not None}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workspace_sessions")
''')

w("workspace_sessions/__init__.py", '''from odin_backend.core.workspace_sessions.workspace_sessions_runtime import WorkspaceSessionsRuntime

__all__ = ["WorkspaceSessionsRuntime"]
''')

# --- operator_focus ---
w("operator_focus/operator_focus_runtime.py", '''"""Operator focus runtime (Prompt 54)."""
from __future__ import annotations
from typing import Any


class OperatorFocusRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._active = False
        self._minutes = 0

    async def start_focus_session(self, *, minutes: int = 45) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_focus_enabled", False):
            return {"accepted": False, "reason": "operator_focus_disabled"}
        self._active = True
        self._minutes = min(minutes, 120)
        self._emit("focus_session_started", {"minutes": self._minutes})
        if hasattr(self._app, "operator_intelligence_v3"):
            await self._app.operator_intelligence_v3.start_deep_focus(minutes=self._minutes)
        return {"accepted": True, "active": True, "minutes": self._minutes, "operator_controlled": True}

    async def estimate_distraction_pressure(self) -> dict[str, Any]:
        pressure = 0.3
        if hasattr(self._app, "window_awareness"):
            snap = self._app.window_awareness.snapshot()
            if snap.get("active", {}).get("app") in ("slack", "discord"):
                pressure = 0.8
        return {"accepted": True, "pressure": pressure, "transparent": True}

    async def detect_focus_breakdown(self) -> dict[str, Any]:
        broken = self._active and self._minutes > 90
        if broken:
            self._emit("focus_breakdown_detected", {"minutes": self._minutes})
        return {"accepted": True, "breakdown": broken}

    async def recommend_focus_recovery(self) -> dict[str, Any]:
        return {"accepted": True, "recommendation": "short_break", "operator_override": True}

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active, "minutes": self._minutes}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_focus")
''')

w("operator_focus/__init__.py", '''from odin_backend.core.operator_focus.operator_focus_runtime import OperatorFocusRuntime

__all__ = ["OperatorFocusRuntime"]
''')

# --- desktop_attention ---
w("desktop_attention/desktop_attention_runtime.py", '''"""Desktop attention runtime (Prompt 54)."""
from __future__ import annotations
from typing import Any


class DesktopAttentionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._salience: dict[str, float] = {"workspace": 0.5, "engineering": 0.4}

    async def prioritize_desktop_attention(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "desktop_attention_enabled", False):
            return {"accepted": False, "reason": "desktop_attention_disabled"}
        if hasattr(self._app, "attention_engine"):
            await self._app.attention_engine.calculate_attention_weights()
        self._emit("desktop_attention_rebalanced", {"salience": self._salience})
        return {"accepted": True, "salience": self._salience, "bounded": True}

    async def compute_workspace_salience(self, *, workspace: str) -> dict[str, Any]:
        score = min(1.0, self._salience.get(workspace, 0.3) + 0.1)
        self._salience[workspace[:40]] = score
        self._emit("workspace_salience_updated", {"workspace": workspace[:40], "score": score})
        return {"accepted": True, "workspace": workspace[:40], "score": score}

    async def suppress_low_priority_surfaces(self) -> dict[str, Any]:
        if hasattr(self._app, "live_overlays_v2"):
            await self._app.live_overlays_v2.suppress_overlay(overlay_type="memory_recall")
        return {"accepted": True, "suppressed_low_priority": True}

    async def rebalance_attention_surfaces(self) -> dict[str, Any]:
        return await self.prioritize_desktop_attention()

    def snapshot(self) -> dict[str, Any]:
        return {"salience": self._salience}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="desktop_attention")
''')

w("desktop_attention/__init__.py", '''from odin_backend.core.desktop_attention.desktop_attention_runtime import DesktopAttentionRuntime

__all__ = ["DesktopAttentionRuntime"]
''')

print("bootstrap_p54_core complete")

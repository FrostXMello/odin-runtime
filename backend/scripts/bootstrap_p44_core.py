"""Bootstrap Prompt 44 persistent cognitive environment modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


SQLITE_STORE = '''
import json
import time
from typing import Any
import aiosqlite

class SqliteTable:
    def __init__(self, conn, table: str) -> None:
        self._conn = conn
        self._table = table

    async def ensure(self) -> None:
        await self._conn.execute(
            f"CREATE TABLE IF NOT EXISTS {self._table} (id INTEGER PRIMARY KEY, payload TEXT, created_at REAL)"
        )
        await self._conn.commit()

    async def insert(self, payload: dict[str, Any]) -> None:
        await self._conn.execute(
            f"INSERT INTO {self._table} (payload, created_at) VALUES (?, ?)",
            (json.dumps(payload), payload.get("created_at", time.time())),
        )
        await self._conn.commit()

    async def recent(self, limit: int = 20) -> list[dict]:
        cur = await self._conn.execute(
            f"SELECT payload FROM {self._table} ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cur.fetchall()
        return [json.loads(r[0]) for r in rows]
'''

# persistent_cognition helpers
for name, body in {
"persistent_cognition/cognition_state_store.py": '''"""SQLite cognition state store."""
from __future__ import annotations
''' + SQLITE_STORE,
"persistent_cognition/continuity_checkpointing.py": '''from __future__ import annotations
from uuid import uuid4

def checkpoint(*, state: dict) -> dict:
    return {"checkpoint_id": str(uuid4()), "keys": list(state.keys())[:20], "created_at": state.get("created_at")}
''',
"persistent_cognition/long_running_threads.py": '''from __future__ import annotations

class LongRunningThreads:
    def __init__(self) -> None:
        self._threads: dict[str, list[dict]] = {}

    def append(self, thread_id: str, item: dict) -> str:
        self._threads.setdefault(thread_id, []).append(item)
        return thread_id

    def get(self, thread_id: str) -> list[dict]:
        return self._threads.get(thread_id, [])
''',
"persistent_cognition/deferred_intentions.py": '''from __future__ import annotations

class DeferredIntentions:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def defer(self, intention: str, priority: float = 0.5) -> dict:
        item = {"intention": intention[:500], "priority": priority}
        self._items.append(item)
        return item

    def pending(self) -> list[dict]:
        return list(self._items)
''',
"persistent_cognition/session_rehydration.py": '''from __future__ import annotations

def rehydrate(*, snapshot: dict) -> dict:
    return {"rehydrated": bool(snapshot), "keys": list(snapshot.keys())[:15]}
''',
"persistent_cognition/cognitive_resume.py": '''from __future__ import annotations

def resume(*, chains: list[dict]) -> dict:
    return {"chains": len(chains), "resumed": bool(chains)}
''',
"persistent_cognition/daemon_snapshots.py": '''from __future__ import annotations
import time

def snapshot(*, uptime_s: float, idle: bool) -> dict:
    return {"uptime_s": uptime_s, "idle": idle, "ts": time.time()}
''',
"persistent_cognition/cognition_recovery.py": '''from __future__ import annotations

def recover(*, checkpoints: list[dict]) -> dict:
    return {"recovered": bool(checkpoints), "count": len(checkpoints)}
''',
"persistent_cognition/persistent_cognition_runtime.py": '''"""Persistent cognitive core orchestrator."""
from __future__ import annotations

import time
from typing import Any

import aiosqlite

from odin_backend.core.persistent_cognition.cognition_recovery import recover
from odin_backend.core.persistent_cognition.cognition_state_store import SqliteTable
from odin_backend.core.persistent_cognition.cognitive_resume import resume
from odin_backend.core.persistent_cognition.continuity_checkpointing import checkpoint
from odin_backend.core.persistent_cognition.daemon_snapshots import snapshot as daemon_snapshot
from odin_backend.core.persistent_cognition.deferred_intentions import DeferredIntentions
from odin_backend.core.persistent_cognition.long_running_threads import LongRunningThreads
from odin_backend.core.persistent_cognition.session_rehydration import rehydrate


class PersistentCognitionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._path = app.settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None
        self._state: SqliteTable | None = None
        self._checkpoints: SqliteTable | None = None
        self._threads = LongRunningThreads()
        self._intentions = DeferredIntentions()

    async def _ensure(self) -> None:
        if self._db:
            return
        self._db = await aiosqlite.connect(self._path)
        self._state = SqliteTable(self._db, "persistent_cognition_state")
        self._checkpoints = SqliteTable(self._db, "cognition_checkpoints")
        await self._state.ensure()
        await self._checkpoints.ensure()

    async def checkpoint(self, *, state: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "persistent_cognition_enabled", False):
            return {"accepted": False, "reason": "persistent_cognition_disabled"}
        await self._ensure()
        payload = {"created_at": time.time(), **(state or {"active": True})}
        cp = checkpoint(state=payload)
        assert self._checkpoints is not None
        await self._checkpoints.insert({**cp, **payload})
        assert self._state is not None
        await self._state.insert(payload)
        self._emit("cognition_checkpoint_created", cp)
        return {"accepted": True, "checkpoint": cp}

    async def rehydrate_session(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "persistent_cognition_enabled", False):
            return {"accepted": False, "reason": "persistent_cognition_disabled"}
        await self._ensure()
        assert self._state is not None
        recent = await self._state.recent(limit=1)
        snap = recent[0] if recent else {}
        rh = rehydrate(snapshot=snap)
        if hasattr(self._app, "daemon_runtime"):
            ds = daemon_snapshot(uptime_s=self._app.daemon_runtime._uptime_s, idle=self._app.daemon_runtime._idle)
            rh["daemon"] = ds
        self._emit("session_rehydrated", rh)
        return {"accepted": True, **rh}

    async def defer_intention(self, *, intention: str) -> dict[str, Any]:
        item = self._intentions.defer(intention)
        assert self._state is not None
        await self._ensure()
        await self._state.insert({"intention": item})
        return {"accepted": True, "intention": item}

    async def resume_cognition(self) -> dict[str, Any]:
        await self._ensure()
        assert self._checkpoints is not None
        cps = await self._checkpoints.recent(limit=5)
        rec = recover(checkpoints=cps)
        r = resume(chains=cps)
        return {"accepted": True, "recovery": rec, "resume": r}

    def snapshot(self) -> dict[str, Any]:
        return {"intentions": len(self._intentions.pending()), "sqlite": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="persistent_cognition")
''',
"persistent_cognition/__init__.py": '''from odin_backend.core.persistent_cognition.persistent_cognition_runtime import PersistentCognitionRuntime
__all__ = ["PersistentCognitionRuntime"]
''',
}.items():
    w(name, body)

print("part1 done")

# daily_continuity
for name, body in {
"daily_continuity/daily_memory.py": '''from __future__ import annotations
import time

def record(*, summary: str) -> dict:
    return {"summary": summary[:300], "day": time.strftime("%Y-%m-%d"), "ts": time.time()}
''',
"daily_continuity/weekly_context.py": '''from __future__ import annotations

def week_context(*, items: list[str]) -> dict:
    return {"items": items[:14], "count": len(items)}
''',
"daily_continuity/continuity_timeline.py": '''from __future__ import annotations

class Timeline:
    def __init__(self) -> None:
        self._events: list[dict] = []

    def add(self, event: dict) -> None:
        self._events.append(event)

    def snapshot(self, limit: int = 30) -> list[dict]:
        return self._events[-limit:]
''',
"daily_continuity/unfinished_work.py": '''from __future__ import annotations

class UnfinishedWork:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def track(self, *, title: str, project: str) -> dict:
        item = {"title": title[:200], "project": project[:80]}
        self._items.append(item)
        return item

    def abandoned(self, *, threshold_h: float = 24) -> list[dict]:
        return self._items
''',
"daily_continuity/project_presence.py": '''from __future__ import annotations

def presence(*, project: str, active: bool) -> dict:
    return {"project": project, "active": active}
''',
"daily_continuity/session_narratives.py": '''from __future__ import annotations

def narrative(*, sessions: list[dict]) -> dict:
    return {"narrative": f"{len(sessions)} recent sessions", "sessions": len(sessions)}
''',
"daily_continuity/continuity_predictions.py": '''from __future__ import annotations

def predict(*, last_action: str) -> dict:
    nxt = "continue debugging" if "debug" in last_action.lower() else "resume project"
    return {"next": nxt, "confidence": 0.7}
''',
"daily_continuity/daily_continuity_runtime.py": '''"""Daily and weekly continuity orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.daily_continuity.continuity_predictions import predict
from odin_backend.core.daily_continuity.continuity_timeline import Timeline
from odin_backend.core.daily_continuity.daily_memory import record
from odin_backend.core.daily_continuity.project_presence import presence
from odin_backend.core.daily_continuity.session_narratives import narrative
from odin_backend.core.daily_continuity.unfinished_work import UnfinishedWork
from odin_backend.core.daily_continuity.weekly_context import week_context


class DailyContinuityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._timeline = Timeline()
        self._unfinished = UnfinishedWork()
        self._last_action = ""

    async def record_day(self, *, summary: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "daily_continuity_enabled", False):
            return {"accepted": False, "reason": "daily_continuity_disabled"}
        mem = record(summary=summary)
        self._timeline.add(mem)
        return {"accepted": True, "memory": mem}

    async def track_unfinished(self, *, title: str, project: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "daily_continuity_enabled", False):
            return {"accepted": False, "reason": "daily_continuity_disabled"}
        item = self._unfinished.track(title=title, project=project)
        self._emit("unfinished_work_detected", item)
        return {"accepted": True, "item": item}

    async def resume_summary(self) -> dict[str, Any]:
        abandoned = self._unfinished.abandoned()
        pred = predict(last_action=self._last_action or "startup")
        self._emit("workflow_prediction_generated", pred)
        return {
            "accepted": True,
            "unfinished": abandoned,
            "prediction": pred,
            "timeline": self._timeline.snapshot(),
            "narrative": narrative(sessions=self._timeline.snapshot(5)),
            "weekly": week_context(items=[e.get("summary", "") for e in self._timeline.snapshot(7)]),
        }

    async def project(self, *, name: str, active: bool = True) -> dict[str, Any]:
        return {"accepted": True, "presence": presence(project=name, active=active)}

    def snapshot(self) -> dict[str, Any]:
        return {"timeline_len": len(self._timeline.snapshot(100)), "unfinished": len(self._unfinished.abandoned())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="daily_continuity")
''',
"daily_continuity/__init__.py": '''from odin_backend.core.daily_continuity.daily_continuity_runtime import DailyContinuityRuntime
__all__ = ["DailyContinuityRuntime"]
''',
}.items():
    w(name, body)

# workspace_presence (deep integration)
for name, body in {
"workspace_presence/live_workspace_graph.py": '''from __future__ import annotations

def graph(*, nodes: list[str]) -> dict:
    return {"nodes": nodes, "edges": max(0, len(nodes) - 1)}
''',
"workspace_presence/active_project_detection.py": '''from __future__ import annotations

def detect(*, repo: str, branch: str) -> dict:
    return {"repo": repo, "branch": branch, "active": True}
''',
"workspace_presence/workflow_state_tracking.py": '''from __future__ import annotations

def track(*, state: str) -> dict:
    return {"state": state, "ts": __import__("time").time()}
''',
"workspace_presence/repository_presence.py": '''from __future__ import annotations

def repo(*, name: str, dirty: bool = False) -> dict:
    return {"name": name, "dirty": dirty}
''',
"workspace_presence/terminal_state_memory.py": '''from __future__ import annotations

class TerminalMemory:
    def __init__(self) -> None:
        self._lines: list[str] = []

    def remember(self, line: str) -> None:
        self._lines.append(line[:200])
        self._lines = self._lines[-50:]

    def snapshot(self) -> list[str]:
        return self._lines[-10:]
''',
"workspace_presence/editor_presence.py": '''from __future__ import annotations

def editor(*, file: str, line: int = 1) -> dict:
    return {"file": file, "line": line}
''',
"workspace_presence/browser_context_bridge.py": '''from __future__ import annotations

def bridge(*, url: str, title: str = "") -> dict:
    return {"url": url[:200], "title": title[:120], "local_only": True}
''',
"workspace_presence/workspace_presence_runtime.py": '''"""Deep workspace integration orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.workspace_presence.active_project_detection import detect
from odin_backend.core.workspace_presence.browser_context_bridge import bridge
from odin_backend.core.workspace_presence.editor_presence import editor
from odin_backend.core.workspace_presence.live_workspace_graph import graph
from odin_backend.core.workspace_presence.repository_presence import repo
from odin_backend.core.workspace_presence.terminal_state_memory import TerminalMemory
from odin_backend.core.workspace_presence.workflow_state_tracking import track


class WorkspacePresenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._terminal = TerminalMemory()
        self._project = ""

    async def observe(self, *, repo: str = "", branch: str = "main", terminal: dict | None = None, ide: dict | None = None, browser: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "workspace_presence_enabled", False):
            return {"accepted": False, "reason": "workspace_presence_disabled"}
        self._project = repo or self._project
        proj = detect(repo=repo or "unknown", branch=branch)
        if terminal and terminal.get("line"):
            self._terminal.remember(str(terminal["line"]))
        nodes = [n for n in [repo, branch, (ide or {}).get("file"), (browser or {}).get("url", "")[:30]] if n]
        g = graph(nodes=nodes)
        if hasattr(self._app, "context_fusion"):
            await self._app.context_fusion.fuse(ide=ide, terminal=terminal, browser=browser)
        if hasattr(self._app, "workstation_awareness"):
            await self._app.workstation_awareness.observe(snapshot={"app": "engineering", "title": repo})
        self._emit("workspace_context_restored", {"repo": repo, "nodes": len(nodes)})
        return {
            "accepted": True,
            "project": proj,
            "repository": repo(name=repo, dirty=bool(terminal)),
            "editor": editor(file=str((ide or {}).get("file", "")), line=int((ide or {}).get("line", 1))),
            "browser": bridge(url=str((browser or {}).get("url", "")), title=str((browser or {}).get("title", ""))),
            "terminal": self._terminal.snapshot(),
            "workflow": track(state="engineering" if repo else "idle"),
            "graph": g,
        }

    async def restore_session(self) -> dict[str, Any]:
        return await self.observe(repo=self._project)

    def snapshot(self) -> dict[str, Any]:
        return {"project": self._project, "terminal_lines": len(self._terminal.snapshot())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workspace_presence")
''',
"workspace_presence/__init__.py": '''from odin_backend.core.workspace_presence.workspace_presence_runtime import WorkspacePresenceRuntime
__all__ = ["WorkspacePresenceRuntime"]
''',
}.items():
    w(name, body)

print("part2 done")

# memory_threads
for name, body in {
"memory_threads/semantic_threads.py": '''from __future__ import annotations

def semantic(*, topic: str) -> dict:
    return {"topic": topic[:120], "kind": "semantic"}
''',
"memory_threads/project_threads.py": '''from __future__ import annotations

def project_thread(*, project: str) -> dict:
    return {"project": project, "kind": "project"}
''',
"memory_threads/conversational_threads.py": '''from __future__ import annotations

def conv_thread(*, thread_id: str) -> dict:
    return {"thread_id": thread_id, "kind": "conversation"}
''',
"memory_threads/thread_linking.py": '''from __future__ import annotations

def link(a: str, b: str) -> dict:
    return {"from": a, "to": b}
''',
"memory_threads/thread_prioritization.py": '''from __future__ import annotations

def prioritize(threads: list[dict]) -> list[dict]:
    return sorted(threads, key=lambda t: t.get("weight", 0), reverse=True)
''',
"memory_threads/thread_decay.py": '''from __future__ import annotations

def decay(*, weight: float, age_h: float) -> float:
    return max(0.0, weight - age_h * 0.01)
''',
"memory_threads/thread_runtime.py": '''"""Persistent memory threads orchestrator."""
from __future__ import annotations
import time
from typing import Any
from uuid import uuid4

from odin_backend.core.memory_threads.conversational_threads import conv_thread
from odin_backend.core.memory_threads.project_threads import project_thread
from odin_backend.core.memory_threads.semantic_threads import semantic
from odin_backend.core.memory_threads.thread_decay import decay
from odin_backend.core.memory_threads.thread_linking import link
from odin_backend.core.memory_threads.thread_prioritization import prioritize


class MemoryThreadsRuntime:
    MAX_THREADS = 64

    def __init__(self, app: Any) -> None:
        self._app = app
        self._threads: dict[str, dict] = {}

    async def activate(self, *, topic: str, project: str = "", thread_id: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "memory_threads_enabled", False):
            return {"accepted": False, "reason": "memory_threads_disabled"}
        tid = thread_id or str(uuid4())
        if len(self._threads) >= self.MAX_THREADS:
            oldest = min(self._threads.values(), key=lambda t: t.get("created_at", 0))
            self._threads = {k: v for k, v in self._threads.items() if v != oldest}
        meta = {**semantic(topic=topic), **project_thread(project=project or topic), "weight": 1.0, "created_at": time.time()}
        self._threads[tid] = meta
        self._emit("memory_thread_activated", {"thread_id": tid, "topic": topic[:80]})
        return {"accepted": True, "thread_id": tid, "meta": meta}

    async def recall(self, *, limit: int = 8) -> dict[str, Any]:
        threads = prioritize(list(self._threads.values()))
        return {"accepted": True, "threads": threads[:limit]}

    async def link_threads(self, *, a: str, b: str) -> dict[str, Any]:
        return {"accepted": True, "link": link(a, b)}

    def snapshot(self) -> dict[str, Any]:
        return {"count": len(self._threads), "max": self.MAX_THREADS}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="memory_threads")
''',
"memory_threads/__init__.py": '''from odin_backend.core.memory_threads.thread_runtime import MemoryThreadsRuntime
__all__ = ["MemoryThreadsRuntime"]
''',
# live_environment
"live_environment/operator_presence_tracking.py": '''from __future__ import annotations

def track(*, active: bool, duration_s: float) -> dict:
    return {"active": active, "duration_s": duration_s}
''',
"live_environment/adaptive_focus_detection.py": '''from __future__ import annotations

def focus(*, switches: int, duration_s: float) -> dict:
    focused = switches < 5 and duration_s > 300
    return {"focused": focused, "switches": switches, "state": "focus" if focused else "distraction"}
''',
"live_environment/workspace_attention_model.py": '''from __future__ import annotations

def attention(*, weight: float) -> dict:
    return {"weight": round(weight, 3)}
''',
"live_environment/interruption_classification.py": '''from __future__ import annotations

def classify(*, reason: str) -> dict:
    urgent = reason in ("error", "mission", "approval")
    return {"reason": reason, "urgent": urgent, "class": "urgent" if urgent else "deferrable"}
''',
"live_environment/environmental_context.py": '''from __future__ import annotations

def context(*, on_battery: bool, heavy_load: bool) -> dict:
    return {"on_battery": on_battery, "heavy_load": heavy_load, "local_only": True}
''',
"live_environment/realtime_context_fusion.py": '''from __future__ import annotations

def fuse(*, signals: list[str]) -> dict:
    return {"signals": signals[:10], "count": len(signals)}
''',
"live_environment/live_environment_runtime.py": '''"""Live personal operating layer."""
from __future__ import annotations
from typing import Any

from odin_backend.core.live_environment.adaptive_focus_detection import focus as detect_focus
from odin_backend.core.live_environment.environmental_context import context as env_context
from odin_backend.core.live_environment.interruption_classification import classify
from odin_backend.core.live_environment.operator_presence_tracking import track
from odin_backend.core.live_environment.realtime_context_fusion import fuse
from odin_backend.core.live_environment.workspace_attention_model import attention


class LiveEnvironmentRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._switches = 0

    async def update(self, *, duration_s: float = 60.0, reason: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "live_environment_enabled", False):
            return {"accepted": False, "reason": "live_environment_disabled"}
        pres = track(active=True, duration_s=duration_s)
        foc = detect_focus(switches=self._switches, duration_s=duration_s)
        attn = attention(weight=0.8 if foc["focused"] else 0.4)
        env = env_context(
            on_battery=getattr(self._app.settings, "on_battery", False),
            heavy_load=getattr(self._app.settings, "heavy_load", False),
        )
        if reason:
            ic = classify(reason=reason)
            self._emit("interruption_classified", ic)
        self._emit("focus_state_changed", foc)
        self._emit("adaptive_presence_updated", pres)
        intensity = "low" if env["on_battery"] or env["heavy_load"] else "normal"
        return {"accepted": True, "presence": pres, "focus": foc, "attention": attn, "environment": env, "intensity": intensity, "fusion": fuse(signals=[reason] if reason else [])}

    async def record_switch(self) -> dict[str, Any]:
        self._switches += 1
        return {"accepted": True, "switches": self._switches}

    def snapshot(self) -> dict[str, Any]:
        return {"switches": self._switches}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_environment")
''',
"live_environment/__init__.py": '''from odin_backend.core.live_environment.live_environment_runtime import LiveEnvironmentRuntime
__all__ = ["LiveEnvironmentRuntime"]
''',
# cognitive_surface
"cognitive_surface/cognition_panels.py": '''from __future__ import annotations

def panels(*, count: int = 4) -> dict:
    return {"panels": min(count, 8), "unified": True}
''',
"cognitive_surface/mission_surface.py": '''from __future__ import annotations

def mission(*, mission_id: str, state: str) -> dict:
    return {"mission_id": mission_id, "state": state}
''',
"cognitive_surface/attention_surface.py": '''from __future__ import annotations

def surface(*, focus: str) -> dict:
    return {"focus": focus[:80]}
''',
"cognitive_surface/reasoning_surface.py": '''from __future__ import annotations

def reasoning(*, steps: list[str]) -> dict:
    return {"steps": steps[:8]}
''',
"cognitive_surface/overlay_compositor.py": '''from __future__ import annotations

def compose(*, layers: list[str]) -> dict:
    return {"layers": layers, "gpu_safe": True}
''',
"cognitive_surface/unified_surface.py": '''"""Unified cognitive surface orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_surface.attention_surface import surface as attn_surface
from odin_backend.core.cognitive_surface.cognition_panels import panels
from odin_backend.core.cognitive_surface.mission_surface import mission
from odin_backend.core.cognitive_surface.overlay_compositor import compose
from odin_backend.core.cognitive_surface.reasoning_surface import reasoning


class CognitiveSurfaceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def render(self, *, mission_id: str = "", focus: str = "workspace", steps: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_surface_enabled", False):
            return {"accepted": False, "reason": "cognitive_surface_disabled"}
        layers = ["presence", "attention", "reasoning"]
        if mission_id:
            layers.append("mission")
        comp = compose(layers=layers)
        surf = {
            "panels": panels(count=4),
            "attention": attn_surface(focus=focus),
            "reasoning": reasoning(steps=steps or ["observe", "plan"]),
            "mission": mission(mission_id=mission_id, state="active") if mission_id else None,
            "compositor": comp,
        }
        self._emit("cognitive_surface_updated", {"layers": len(layers)})
        return {"accepted": True, "surface": surf, "gpu_safe": True}

    def snapshot(self) -> dict[str, Any]:
        return {"unified": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_surface")
''',
"cognitive_surface/__init__.py": '''from odin_backend.core.cognitive_surface.unified_surface import CognitiveSurfaceRuntime
__all__ = ["CognitiveSurfaceRuntime"]
''',
}.items():
    w(name, body)

print("bootstrap_p44 complete")

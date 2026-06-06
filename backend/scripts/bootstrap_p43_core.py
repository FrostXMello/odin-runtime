"""Bootstrap Prompt 43 native cognitive desktop modules."""
from __future__ import annotations

import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


OS_NAME = platform.system().lower()

# --- native_shell ---
for name, body in {
"native_shell/desktop_shell.py": '''"""Lightweight desktop shell adapter."""
from __future__ import annotations
import platform
from typing import Any

PLATFORMS = ("windows", "darwin", "linux")

def detect_platform() -> str:
    s = platform.system().lower()
    if "windows" in s:
        return "windows"
    if "darwin" in s:
        return "darwin"
    return "linux"

def shell_state(*, visible: bool = True) -> dict[str, Any]:
    return {"platform": detect_platform(), "visible": visible, "local_only": True, "adapter": "lightweight"}
''',
"native_shell/workspace_surface.py": '''from __future__ import annotations
from typing import Any

def surface(*, app: str, title: str = "") -> dict[str, Any]:
    return {"app": app, "title": title[:120], "focused": True}
''',
"native_shell/command_palette.py": '''from __future__ import annotations
from typing import Any

def palette(*, query: str, workspace: dict | None = None) -> dict[str, Any]:
    ws = workspace or {}
    actions = ["open mission", "run benchmark", "toggle focus mode", "restore session"]
    matched = [a for a in actions if query.lower() in a or not query]
    return {"query": query[:80], "actions": matched[:8], "workspace_app": ws.get("active_app", "unknown")}
''',
"native_shell/quick_actions.py": '''from __future__ import annotations

ACTIONS = ("assist", "debug", "mission", "voice", "focus")

def quick(action: str) -> dict:
    a = action if action in ACTIONS else "assist"
    return {"action": a, "supervised": True}
''',
"native_shell/dock_runtime.py": '''from __future__ import annotations

def dock(*, items: list[str] | None = None) -> dict:
    return {"items": items or ["cognition", "missions", "engineering", "voice"], "tray": True}
''',
"native_shell/session_bar.py": '''from __future__ import annotations

def bar(*, missions: int = 0, status: str = "ready") -> dict:
    return {"missions": missions, "status": status, "cognitive_online": True}
''',
"native_shell/runtime_presence.py": '''from __future__ import annotations

def presence(*, energy: float = 0.5) -> dict:
    return {"energy": round(energy, 3), "simulated": True, "disclosure": "runtime_presence"}
''',
"native_shell/native_shell_runtime.py": '''"""Native cognitive desktop shell orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.native_shell.command_palette import palette
from odin_backend.core.native_shell.desktop_shell import shell_state
from odin_backend.core.native_shell.dock_runtime import dock
from odin_backend.core.native_shell.quick_actions import quick
from odin_backend.core.native_shell.runtime_presence import presence
from odin_backend.core.native_shell.session_bar import bar
from odin_backend.core.native_shell.workspace_surface import surface


class NativeShellRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._shell = shell_state()
        self._notifications: list[dict] = []

    async def activate(self, *, workspace: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_shell_enabled", False):
            return {"accepted": False, "reason": "native_shell_disabled"}
        ws = workspace or {}
        surf = surface(app=ws.get("active_app", "desktop"), title=ws.get("title", ""))
        pal = palette(query="", workspace=ws)
        missions = 0
        if hasattr(self._app, "mission_manager"):
            missions = len(getattr(self._app.mission_manager, "_missions", {}) or {})
        self._emit("cognitive_surface_rendered", {"platform": self._shell["platform"]})
        self._emit("persistent_presence_updated", presence(energy=0.6))
        self._emit("workspace_focus_changed", {"app": surf["app"]})
        return {
            "accepted": True,
            "shell": self._shell,
            "surface": surf,
            "palette": pal,
            "dock": dock(),
            "session_bar": bar(missions=missions),
            "presence": presence(),
        }

    async def command(self, *, query: str, workspace: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_shell_enabled", False):
            return {"accepted": False, "reason": "native_shell_disabled"}
        return {"accepted": True, "palette": palette(query=query, workspace=workspace)}

    async def quick_action(self, *, action: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_shell_enabled", False):
            return {"accepted": False, "reason": "native_shell_disabled"}
        return {"accepted": True, **quick(action)}

    async def notify(self, *, title: str, body: str) -> dict[str, Any]:
        n = {"title": title[:80], "body": body[:200], "local_only": True}
        self._notifications.append(n)
        return {"accepted": True, "notification": n}

    def snapshot(self) -> dict[str, Any]:
        return {"shell": self._shell, "notifications": len(self._notifications)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="native_shell")
''',
"native_shell/__init__.py": '''from odin_backend.core.native_shell.native_shell_runtime import NativeShellRuntime
__all__ = ["NativeShellRuntime"]
''',
}.items():
    w(name, body)

# --- immersive_ui ---
for name, body in {
"immersive_ui/dynamic_layouts.py": '''MODES = ("minimal", "balanced", "immersive", "cinematic")

def layout(mode: str = "balanced") -> dict:
    m = mode if mode in MODES else "balanced"
    cols = {"minimal": 1, "balanced": 2, "immersive": 3, "cinematic": 4}.get(m, 2)
    return {"mode": m, "columns": cols, "fps_cap": {"minimal": 15, "balanced": 30, "immersive": 45, "cinematic": 60}.get(m, 30)}
''',
"immersive_ui/cognitive_animation.py": '''def animation(*, thinking: bool) -> dict:
    return {"thinking": thinking, "style": "pulse" if thinking else "idle", "gpu_safe": True}
''',
"immersive_ui/focus_modes.py": '''def focus(*, distraction_free: bool) -> dict:
    return {"distraction_free": distraction_free, "overlays_minimal": distraction_free}
''',
"immersive_ui/adaptive_panels.py": '''def panels(*, count: int = 3) -> dict:
    return {"panels": min(count, 6), "draggable": True}
''',
"immersive_ui/cinematic_mode.py": '''def cinematic(enabled: bool) -> dict:
    return {"enabled": enabled, "fps_cap": 60 if enabled else 30, "progressive_render": enabled}
''',
"immersive_ui/ambient_presence.py": '''def ambient(*, idle: bool) -> dict:
    return {"idle": idle, "glow": not idle, "simulated": True}
''',
"immersive_ui/immersive_runtime.py": '''"""Immersive cognitive UI orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.immersive_ui.adaptive_panels import panels
from odin_backend.core.immersive_ui.ambient_presence import ambient
from odin_backend.core.immersive_ui.cinematic_mode import cinematic
from odin_backend.core.immersive_ui.cognitive_animation import animation
from odin_backend.core.immersive_ui.dynamic_layouts import MODES, layout
from odin_backend.core.immersive_ui.focus_modes import focus


class ImmersiveUiRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        mode = getattr(app.settings, "native_desktop_mode", "balanced")
        self._mode = mode if mode in MODES else "balanced"

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "immersive_ui_enabled", False):
            return {"accepted": False, "reason": "immersive_ui_disabled"}
        self._mode = mode if mode in MODES else "balanced"
        lay = layout(self._mode)
        self._emit("immersive_mode_changed", {"mode": self._mode, "fps_cap": lay["fps_cap"]})
        return {"accepted": True, "layout": lay, "animation": animation(thinking=False), "focus": focus(distraction_free=self._mode == "minimal")}

    async def render(self, *, thinking: bool = False, idle: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "immersive_ui_enabled", False):
            return {"accepted": False, "reason": "immersive_ui_disabled"}
        lay = layout(self._mode)
        return {
            "accepted": True,
            "mode": self._mode,
            "layout": lay,
            "animation": animation(thinking=thinking),
            "panels": panels(count=lay["columns"]),
            "cinematic": cinematic(self._mode == "cinematic"),
            "ambient": ambient(idle=idle),
            "gpu_safe": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "modes": list(MODES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="immersive_ui")
''',
"immersive_ui/__init__.py": '''from odin_backend.core.immersive_ui.immersive_runtime import ImmersiveUiRuntime
__all__ = ["ImmersiveUiRuntime"]
''',
}.items():
    w(name, body)

print("part 1 done")

# --- daemon extensions ---
for name, body in {
"daemon/persistent_presence.py": '''from __future__ import annotations
import time

def update(*, active: bool) -> dict:
    return {"active": active, "ts": time.time(), "simulated": True}
''',
"daemon/cognition_scheduler.py": '''from __future__ import annotations

def schedule(*, idle: bool, survival_mode: str = "balanced") -> dict:
    interval = 30 if idle else 5
    if survival_mode == "overnight_daemon":
        interval = 120 if idle else 15
    return {"interval_s": interval, "bounded": True}
''',
"daemon/wake_intelligence.py": '''from __future__ import annotations

def wake(*, wakeword: str = "", energy: float = 0.5) -> dict:
    triggered = energy > 0.55 or wakeword.lower() in ("odin", "hey odin")
    return {"triggered": triggered, "wakeword": wakeword[:32], "local_only": True}
''',
"daemon/deferred_reasoning.py": '''from __future__ import annotations

class DeferredQueue:
    def __init__(self) -> None:
        self._items: list[str] = []

    def defer(self, thought: str) -> dict:
        self._items.append(thought[:500])
        return {"queued": len(self._items)}

    def drain(self, limit: int = 5) -> list[str]:
        out = self._items[:limit]
        self._items = self._items[limit:]
        return out
''',
"daemon/realtime_attention.py": '''from __future__ import annotations

def attention(*, focus: str, weight: float = 0.5) -> dict:
    return {"focus": focus[:80], "weight": round(weight, 3)}
''',
"daemon/operator_interrupts.py": '''from __future__ import annotations

def interrupt(*, reason: str = "operator") -> dict:
    return {"interrupted": True, "reason": reason[:80], "recovery": True}
''',
}.items():
    w(name, body)

# --- live_engineering ---
for name, body in {
"live_engineering/realtime_repo_awareness.py": '''from __future__ import annotations
from typing import Any

def observe(*, repo: str, branch: str = "main", dirty: bool = False) -> dict[str, Any]:
    return {"repo": repo, "branch": branch, "dirty": dirty, "engineering_active": True}
''',
"live_engineering/live_debug_assistant.py": '''from __future__ import annotations

def assist(*, error: str) -> dict:
    hints = ["check stack trace", "run isolated tests", "inspect recent patches"]
    if "ImportError" in error:
        hints.insert(0, "verify module path")
    return {"error": error[:200], "hints": hints[:5], "supervised": True}
''',
"live_engineering/terminal_reasoning.py": '''from __future__ import annotations

def reason(*, line: str) -> dict:
    return {"line": line[:200], "inference": "engineering session" if "pytest" in line else "general"}
''',
"live_engineering/live_patch_assist.py": '''from __future__ import annotations

def suggest(*, file: str, issue: str) -> dict:
    return {"file": file, "issue": issue[:120], "approval_required": True, "no_main_commit": True}
''',
"live_engineering/workflow_guidance.py": '''from __future__ import annotations

def guide(*, step: str) -> dict:
    return {"step": step, "next": "validate" if step == "patch" else "test"}
''',
"live_engineering/architecture_assistant.py": '''from __future__ import annotations

def advise(*, component: str) -> dict:
    return {"component": component, "note": "preserve incremental extension", "supervised": True}
''',
"live_engineering/engineering_presence.py": '''from __future__ import annotations
from typing import Any

from odin_backend.core.live_engineering.architecture_assistant import advise
from odin_backend.core.live_engineering.live_debug_assistant import assist
from odin_backend.core.live_engineering.live_patch_assist import suggest
from odin_backend.core.live_engineering.realtime_repo_awareness import observe
from odin_backend.core.live_engineering.terminal_reasoning import reason
from odin_backend.core.live_engineering.workflow_guidance import guide


class LiveEngineeringRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._repo = ""

    async def session(self, *, repo: str, terminal: dict | None = None, ide: dict | None = None, error: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "live_engineering_enabled", False):
            return {"accepted": False, "reason": "live_engineering_disabled"}
        self._repo = repo
        obs = observe(repo=repo, branch=terminal.get("branch", "main") if terminal else "main")
        if hasattr(self._app, "context_fusion"):
            await self._app.context_fusion.fuse(ide=ide, terminal=terminal)
        if hasattr(self._app, "workstation_awareness"):
            await self._app.workstation_awareness.observe(snapshot={"app": "engineering", "title": repo})
        dbg = assist(error=error) if error else {"hints": []}
        term = reason(line=str((terminal or {}).get("line", "")))
        self._emit("live_engineering_detected", {"repo": repo})
        if error:
            patch = suggest(file=str((ide or {}).get("file", "unknown")), issue=error)
            self._emit("live_patch_suggested", patch)
        return {
            "accepted": True,
            "repo": obs,
            "debug": dbg,
            "terminal": term,
            "guidance": guide(step="debug" if error else "observe"),
            "architecture": advise(component=repo),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"repo": self._repo}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_engineering")
''',
"live_engineering/__init__.py": '''from odin_backend.core.live_engineering.engineering_presence import LiveEngineeringRuntime
__all__ = ["LiveEngineeringRuntime"]
''',
}.items():
    w(name, body)

# --- conversational_os ---
for name, body in {
"conversational_os/natural_command_router.py": '''from __future__ import annotations
from typing import Any

COMMANDS = ("mission", "benchmark", "focus", "debug", "status", "restore")

def route(*, text: str) -> dict[str, Any]:
    lower = text.lower()
    for c in COMMANDS:
        if c in lower:
            return {"command": c, "confidence": 0.8, "text": text[:200]}
    return {"command": "chat", "confidence": 0.5, "text": text[:200]}
''',
"conversational_os/conversational_memory.py": '''from __future__ import annotations

class ConvMemory:
    def __init__(self) -> None:
        self._turns: list[dict] = []

    def add(self, role: str, content: str) -> None:
        self._turns.append({"role": role, "content": content[:2000]})

    def context(self, limit: int = 8) -> list[dict]:
        return self._turns[-limit:]
''',
"conversational_os/persistent_threads.py": '''from __future__ import annotations
from uuid import uuid4

class ThreadStore:
    def __init__(self) -> None:
        self._threads: dict[str, list[dict]] = {}

    def append(self, thread_id: str, msg: dict) -> str:
        tid = thread_id or str(uuid4())
        self._threads.setdefault(tid, []).append(msg)
        return tid

    def restore(self, thread_id: str) -> dict:
        msgs = self._threads.get(thread_id, [])
        return {"thread_id": thread_id, "messages": msgs, "restored": bool(msgs)}
''',
"conversational_os/contextual_intents.py": '''from __future__ import annotations

def intent(*, workspace: dict | None = None) -> dict:
    ws = workspace or {}
    if ws.get("debugging"):
        return {"intent": "debugging", "confidence": 0.85}
    return {"intent": "general", "confidence": 0.6}
''',
"conversational_os/multi_modal_sessions.py": '''from __future__ import annotations

def session(*, voice: bool = False, text: bool = True) -> dict:
    return {"modalities": [m for m, on in (("voice", voice), ("text", text)) if on], "unified": True}
''',
"conversational_os/conversational_runtime.py": '''"""Conversational operating layer orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.conversational_os.contextual_intents import intent
from odin_backend.core.conversational_os.conversational_memory import ConvMemory
from odin_backend.core.conversational_os.multi_modal_sessions import session
from odin_backend.core.conversational_os.natural_command_router import route
from odin_backend.core.conversational_os.persistent_threads import ThreadStore


class ConversationalOSRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._memory = ConvMemory()
        self._threads = ThreadStore()

    async def interact(self, *, text: str, workspace: dict | None = None, thread_id: str = "", voice: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "conversational_os_enabled", False):
            return {"accepted": False, "reason": "conversational_os_disabled"}
        cmd = route(text=text)
        self._memory.add("user", text)
        resp = f"Routing to {cmd['command']}: acknowledged."
        if hasattr(self._app, "conversation"):
            chat = await self._app.conversation.chat(prompt=text, context=workspace or {})
            resp = chat.get("response", resp)
        self._memory.add("assistant", resp)
        tid = self._threads.append(thread_id, {"role": "user", "content": text})
        self._threads.append(tid, {"role": "assistant", "content": resp})
        self._emit("reasoning_stream_updated", {"command": cmd["command"]})
        return {
            "accepted": True,
            "command": cmd,
            "response": resp,
            "intent": intent(workspace=workspace),
            "session": session(voice=voice),
            "thread_id": tid,
            "supervised": True,
        }

    async def restore(self, *, thread_id: str) -> dict[str, Any]:
        restored = self._threads.restore(thread_id)
        if restored["restored"]:
            self._emit("conversational_context_restored", {"thread_id": thread_id})
        return {"accepted": True, **restored}

    def snapshot(self) -> dict[str, Any]:
        return {"turns": len(self._memory._turns)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="conversational_os")
''',
"conversational_os/__init__.py": '''from odin_backend.core.conversational_os.conversational_runtime import ConversationalOSRuntime
__all__ = ["ConversationalOSRuntime"]
''',
}.items():
    w(name, body)

# --- reasoning_streams ---
for name, body in {
"reasoning_streams/thought_renderer.py": '''from __future__ import annotations

def render(*, text: str) -> dict:
    return {"text": text[:500], "transparent": True, "simulated": False}
''',
"reasoning_streams/reasoning_pipeline.py": '''from __future__ import annotations

def pipeline(*, steps: list[str]) -> dict:
    return {"steps": steps[:12], "explainable": True}
''',
"reasoning_streams/stream_summarizer.py": '''from __future__ import annotations

def summarize(*, items: list[str]) -> dict:
    return {"summary": "; ".join(items[:4])[:300], "count": len(items)}
''',
"reasoning_streams/cognitive_heatmaps.py": '''from __future__ import annotations

def heatmap(*, zones: dict) -> dict:
    return {"zones": zones, "max": max(zones.values()) if zones else 0}
''',
"reasoning_streams/mission_visualizer.py": '''from __future__ import annotations

def visualize(*, mission_id: str, state: str) -> dict:
    return {"mission_id": mission_id, "state": state, "nodes": 3}
''',
"reasoning_streams/live_decision_graph.py": '''from __future__ import annotations

def graph(*, decisions: list[str]) -> dict:
    return {"nodes": decisions[:8], "edges": max(0, len(decisions) - 1)}
''',
"reasoning_streams/streams_runtime.py": '''"""Visual reasoning streams orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.reasoning_streams.cognitive_heatmaps import heatmap
from odin_backend.core.reasoning_streams.live_decision_graph import graph
from odin_backend.core.reasoning_streams.mission_visualizer import visualize
from odin_backend.core.reasoning_streams.reasoning_pipeline import pipeline
from odin_backend.core.reasoning_streams.stream_summarizer import summarize
from odin_backend.core.reasoning_streams.thought_renderer import render


class ReasoningStreamsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._items: list[str] = []

    async def push(self, *, thought: str, steps: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "reasoning_streams_enabled", False):
            return {"accepted": False, "reason": "reasoning_streams_disabled"}
        self._items.append(thought)
        r = render(text=thought)
        pipe = pipeline(steps=steps or ["observe", "reason", "respond"])
        self._emit("reasoning_stream_updated", {"items": len(self._items)})
        return {
            "accepted": True,
            "rendered": r,
            "pipeline": pipe,
            "summary": summarize(items=self._items),
            "heatmap": heatmap(zones={"cognition": 0.7, "memory": 0.4, "execution": 0.5}),
            "decisions": graph(decisions=steps or ["observe", "act"]),
            "transparent": True,
        }

    async def mission(self, *, mission_id: str, state: str = "active") -> dict[str, Any]:
        viz = visualize(mission_id=mission_id, state=state)
        return {"accepted": True, "mission": viz}

    def snapshot(self) -> dict[str, Any]:
        return {"items": len(self._items)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="reasoning_streams")
''',
"reasoning_streams/__init__.py": '''from odin_backend.core.reasoning_streams.streams_runtime import ReasoningStreamsRuntime
__all__ = ["ReasoningStreamsRuntime"]
''',
}.items():
    w(name, body)

print("bootstrap_p43 complete")

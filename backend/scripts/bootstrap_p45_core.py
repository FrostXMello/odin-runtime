"""Bootstrap Prompt 45 cognitive desktop experience modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


MODES = ("compact", "balanced", "immersive", "cinematic")

# desktop_client runtime
w("desktop_client/session_store.py", '''from __future__ import annotations
import json
import time
from pathlib import Path

def save_session(*, path: str, data: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {**data, "saved_at": time.time()}
    p.write_text(json.dumps(payload), encoding="utf-8")
    return {"saved": True, "path": str(p)}

def load_session(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "data": json.loads(p.read_text(encoding="utf-8"))}
''')

w("desktop_client/desktop_client_runtime.py", '''"""Desktop client session orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.desktop_client.session_store import load_session, save_session

MODES = ("compact", "balanced", "immersive", "cinematic")


class DesktopClientRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = getattr(app.settings, "native_desktop_mode", "balanced")
        self._session_path = "./data/desktop_session.json"

    async def connect(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "desktop_client_enabled", False):
            return {"accepted": False, "reason": "desktop_client_enabled_disabled"}
        restored = load_session(path=self._session_path)
        if restored.get("restored"):
            self._emit("desktop_session_restored", {"mode": self._mode})
        return {
            "accepted": True,
            "mode": self._mode,
            "modes": list(MODES),
            "local_backend": True,
            "session": restored,
        }

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if mode not in MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        save_session(path=self._session_path, data={"mode": mode})
        return {"accepted": True, "mode": mode, "fps_cap": {"compact": 15, "balanced": 30, "immersive": 45, "cinematic": 60}.get(mode, 30)}

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="desktop_client")
''')

w("desktop_client/__init__.py", '''from odin_backend.core.desktop_client.desktop_client_runtime import DesktopClientRuntime
__all__ = ["DesktopClientRuntime"]
''')

# conversation_workspace
w("conversation_workspace/workspace_runtime.py", '''"""Unified chat + cognitive stream workspace."""
from __future__ import annotations
from typing import Any
from uuid import uuid4


class ConversationWorkspaceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._workspace_id = str(uuid4())
        self._panels = ["chat", "thought_stream", "reasoning", "missions", "agents", "context", "memory"]

    async def open(self, *, thread_id: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "conversation_workspace_enabled", False):
            return {"accepted": False, "reason": "conversation_workspace_disabled"}
        chat = {}
        if hasattr(self._app, "conversational_os"):
            chat = await self._app.conversational_os.interact(text="workspace open", thread_id=thread_id)
        streams = {}
        if hasattr(self._app, "reasoning_streams"):
            streams = await self._app.reasoning_streams.push(thought="workspace active")
        self._emit("conversation_workspace_opened", {"workspace_id": self._workspace_id})
        return {
            "accepted": True,
            "workspace_id": self._workspace_id,
            "panels": self._panels,
            "chat": chat,
            "streams": streams,
            "approval_inline": True,
            "supervised": True,
        }

    async def interact(self, *, text: str, context: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "conversation_workspace_enabled", False):
            return {"accepted": False, "reason": "conversation_workspace_disabled"}
        resp = {}
        if hasattr(self._app, "conversational_os"):
            resp = await self._app.conversational_os.interact(text=text, workspace=context or {})
        if hasattr(self._app, "conversation"):
            await self._app.conversation.chat(prompt=text, context=context)
        self._emit("live_reasoning_rendered", {"text_len": len(text)})
        return {"accepted": True, "response": resp, "streaming": True}

    def snapshot(self) -> dict[str, Any]:
        return {"workspace_id": self._workspace_id, "panels": self._panels}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="conversation_workspace")
''')

w("conversation_workspace/__init__.py", '''from odin_backend.core.conversation_workspace.workspace_runtime import ConversationWorkspaceRuntime
__all__ = ["ConversationWorkspaceRuntime"]
''')

# live_visualization
w("live_visualization/visualization_runtime.py", '''"""Live cognitive visualization orchestrator."""
from __future__ import annotations
from typing import Any


class LiveVisualizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._fps_cap = 30

    async def render(self, *, view: str = "reasoning_dag") -> dict[str, Any]:
        if not getattr(self._app.settings, "live_visualization_enabled", False):
            return {"accepted": False, "reason": "live_visualization_disabled"}
        mode = getattr(self._app.settings, "native_desktop_mode", "balanced")
        self._fps_cap = {"compact": 15, "balanced": 30, "immersive": 45, "cinematic": 60}.get(mode, 30)
        graph = {"nodes": [], "edges": []}
        if hasattr(self._app, "reasoning_streams"):
            r = await self._app.reasoning_streams.push(thought=f"viz:{view}")
            graph = r.get("decisions", graph)
        society = {"agents": []}
        if hasattr(self._app, "agent_society"):
            society = {"agents": list(getattr(self._app.agent_society, "_agents", {}).keys())[:8]}
        self._emit("visualization_synced", {"view": view, "fps_cap": self._fps_cap})
        self._emit("live_reasoning_rendered", {"view": view})
        return {
            "accepted": True,
            "view": view,
            "graph": graph,
            "society": society,
            "fps_cap": self._fps_cap,
            "lazy_render": True,
            "gpu_safe": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"fps_cap": self._fps_cap}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_visualization")
''')

w("live_visualization/__init__.py", '''from odin_backend.core.live_visualization.visualization_runtime import LiveVisualizationRuntime
__all__ = ["LiveVisualizationRuntime"]
''')

# voice_desktop
w("voice_desktop/voice_desktop_coordinator.py", '''"""Desktop-first voice experience coordinator."""
from __future__ import annotations
from typing import Any

VOICE_MODES = ("passive", "assistant", "immersive", "daemon")


class VoiceDesktopCoordinator:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "assistant"

    async def listen(self, *, text: str, energy: float = 0.6, push_to_talk: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "voice_desktop_enabled", False):
            return {"accepted": False, "reason": "voice_desktop_disabled"}
        if not getattr(self._app.settings, "realtime_voice_enabled", False):
            return {"accepted": False, "reason": "realtime_voice_disabled"}
        resp = await self._app.realtime_voice.process_utterance(text=text, energy=energy)
        if hasattr(self._app, "daemon_runtime") and self._mode == "daemon":
            await self._app.daemon_runtime.cognitive_tick(wakeword="odin", energy=energy)
        return {"accepted": True, "voice": resp, "mode": self._mode, "push_to_talk": push_to_talk, "subtitles": True}

    async def interrupt(self) -> dict[str, Any]:
        hit = self._app.realtime_voice.interrupt()
        if hasattr(self._app, "daemon_runtime"):
            await self._app.daemon_runtime.handle_interrupt(reason="voice")
        self._emit("voice_interrupt_detected", hit if isinstance(hit, dict) else {"interrupted": True})
        return {"accepted": True, "interrupt": hit}

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if mode not in VOICE_MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        return {"accepted": True, "mode": mode}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "modes": list(VOICE_MODES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="voice_desktop")
''')

w("voice_desktop/__init__.py", '''from odin_backend.core.voice_desktop.voice_desktop_coordinator import VoiceDesktopCoordinator
__all__ = ["VoiceDesktopCoordinator"]
''')

# daily_operator_experience
w("daily_operator_experience/operator_experience_runtime.py", '''"""Daily driver desktop experience orchestrator."""
from __future__ import annotations
from typing import Any


class DailyOperatorExperienceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def startup(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "daily_operator_experience_enabled", False):
            return {"accepted": False, "reason": "daily_operator_experience_disabled"}
        briefing = {}
        if hasattr(self._app, "daily_workflow"):
            briefing = await self._app.daily_workflow.startup_routine()
        rehydrated = {}
        if hasattr(self._app, "persistent_cognition"):
            rehydrated = await self._app.persistent_cognition.rehydrate_session()
            self._emit("workspace_rehydrated", rehydrated)
        workspace = {}
        if hasattr(self._app, "workspace_presence"):
            workspace = await self._app.workspace_presence.restore_session()
        continuity = {}
        if hasattr(self._app, "daily_continuity"):
            continuity = await self._app.daily_continuity.resume_summary()
        return {
            "accepted": True,
            "briefing": briefing,
            "rehydrated": rehydrated,
            "workspace": workspace,
            "continuity": continuity,
            "morning_summary": continuity.get("narrative"),
        }

    async def focus_shift(self, *, focus: str) -> dict[str, Any]:
        self._emit("operator_focus_shifted", {"focus": focus[:80]})
        if hasattr(self._app, "live_environment"):
            await self._app.live_environment.update(duration_s=120, reason=focus)
        return {"accepted": True, "focus": focus}

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": getattr(self._app.settings, "daily_operator_experience_enabled", False)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="daily_operator_experience")
''')

w("daily_operator_experience/__init__.py", '''from odin_backend.core.daily_operator_experience.operator_experience_runtime import DailyOperatorExperienceRuntime
__all__ = ["DailyOperatorExperienceRuntime"]
''')

# desktop_overlay
w("desktop_overlay/overlay_runtime.py", '''"""Floating desktop overlay orchestrator."""
from __future__ import annotations
from typing import Any

OVERLAY_KINDS = ("terminal", "debug", "mission_hud", "subtitles", "memory_hint", "workflow")


class DesktopOverlayRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._attached: list[str] = []

    async def attach(self, *, kind: str, context: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "desktop_overlay_enabled", False):
            return {"accepted": False, "reason": "desktop_overlay_disabled"}
        k = kind if kind in OVERLAY_KINDS else "workflow"
        self._attached.append(k)
        panel = {"kind": k, "movable": True, "transparent": True, "local_only": True}
        if hasattr(self._app, "live_overlay"):
            ext = await self._app.live_overlay.render(context=context or {}, mode="assistive")
            panel["live_overlay"] = ext.get("panels", {})
        self._emit("overlay_attached", {"kind": k})
        return {"accepted": True, "overlay": panel, "attached": self._attached[-6:]}

    async def memory_surface(self) -> dict[str, Any]:
        threads = {}
        if hasattr(self._app, "memory_threads"):
            threads = await self._app.memory_threads.recall()
        self._emit("memory_surface_rendered", {"threads": len(threads.get("threads", []))})
        return {"accepted": True, "memory": threads}

    def snapshot(self) -> dict[str, Any]:
        return {"attached": self._attached}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="desktop_overlay")
''')

w("desktop_overlay/__init__.py", '''from odin_backend.core.desktop_overlay.overlay_runtime import DesktopOverlayRuntime
__all__ = ["DesktopOverlayRuntime"]
''')

print("bootstrap_p45 complete")

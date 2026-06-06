"""Bootstrap Prompt 46 unified cognitive operating environment modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


EMIT = '''
    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="{component}")
'''

PROFILES = ("ultra_light", "balanced", "immersive", "cinematic")
WORKSPACE_MODES = ("minimal", "operator", "engineering", "immersive", "cinematic")

# --- cognitive_workspace ---
w("cognitive_workspace/workspace_state.py", '''from __future__ import annotations
import json
import time
from pathlib import Path

def save_layout(*, path: str, layout: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {**layout, "saved_at": time.time()}
    p.write_text(json.dumps(payload), encoding="utf-8")
    return {"saved": True}

def load_layout(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False, "panels": []}
    data = json.loads(p.read_text(encoding="utf-8"))
    return {"restored": True, "layout": data}
''')

w("cognitive_workspace/layout_engine.py", '''from __future__ import annotations
from typing import Any

DEFAULT_PANELS = [
    "chat", "thought_stream", "reasoning", "missions", "agents",
    "memory_timeline", "voice_dock", "command_palette",
]


def build_layout(*, mode: str, panels: list[str] | None = None) -> dict[str, Any]:
    base = panels or DEFAULT_PANELS
    cols = {"minimal": 1, "operator": 2, "engineering": 3, "immersive": 3, "cinematic": 4}.get(mode, 2)
    return {"mode": mode, "columns": cols, "panels": base, "draggable": True, "persistent": True}
''')

w("cognitive_workspace/attention_router.py", '''from __future__ import annotations
from typing import Any


def route_attention(*, focus: str, panels: list[str]) -> dict[str, Any]:
    primary = panels[0] if panels else "chat"
    if "reasoning" in focus.lower():
        primary = "reasoning"
    elif "mission" in focus.lower():
        primary = "missions"
    return {"primary_panel": primary, "focus": focus[:120]}
''')

w("cognitive_workspace/cognitive_focus.py", '''from __future__ import annotations
from typing import Any

IMMERSIVE = ("minimal", "operator", "engineering", "immersive", "cinematic")


def focus_profile(mode: str) -> dict[str, Any]:
    fps = {"minimal": 15, "operator": 24, "engineering": 30, "immersive": 45, "cinematic": 60}
    return {
        "mode": mode if mode in IMMERSIVE else "operator",
        "fps_cap": fps.get(mode, 30),
        "fullscreen_cognition": mode in ("immersive", "cinematic"),
        "split_reasoning": mode in ("engineering", "immersive", "cinematic"),
    }
''')

w("cognitive_workspace/live_panels.py", '''from __future__ import annotations
from typing import Any


def panel_snapshot(*, app: Any) -> dict[str, Any]:
    agents = []
    if hasattr(app, "agent_society"):
        agents = list(getattr(app.agent_society, "_agents", {}).keys())[:12]
    missions = []
    if hasattr(app, "mission_manager"):
        missions = [getattr(m, "mission_id", str(i)) for i, m in enumerate(getattr(app.mission_manager, "_missions", {}).values())][:8]
    return {"agents": agents, "missions": missions, "live": True}
''')

w("cognitive_workspace/session_layouts.py", '''from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_workspace.workspace_state import load_layout, save_layout


class SessionLayouts:
    def __init__(self, path: str = "./data/cognitive_workspace_layout.json") -> None:
        self._path = path

    def persist(self, layout: dict) -> dict[str, Any]:
        return save_layout(path=self._path, layout=layout)

    def restore(self) -> dict[str, Any]:
        return load_layout(path=self._path)
''')

w("cognitive_workspace/workspace_runtime.py", '''"""Unified cognitive workspace orchestrator (Prompt 46)."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

from odin_backend.core.cognitive_workspace.attention_router import route_attention
from odin_backend.core.cognitive_workspace.cognitive_focus import focus_profile
from odin_backend.core.cognitive_workspace.layout_engine import build_layout
from odin_backend.core.cognitive_workspace.live_panels import panel_snapshot
from odin_backend.core.cognitive_workspace.session_layouts import SessionLayouts

WORKSPACE_MODES = ("minimal", "operator", "engineering", "immersive", "cinematic")
RESOURCE_PROFILES = ("ultra_light", "balanced", "immersive", "cinematic")


class CognitiveWorkspaceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._id = str(uuid4())
        self._mode = "operator"
        self._profile = "balanced"
        self._layouts = SessionLayouts()
        self._panels = build_layout(mode=self._mode)["panels"]

    async def open(self, *, mode: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_workspace_enabled", False):
            return {"accepted": False, "reason": "cognitive_workspace_disabled"}
        if mode in WORKSPACE_MODES:
            self._mode = mode
        layout = build_layout(mode=self._mode, panels=self._panels)
        restored = self._layouts.restore()
        if restored.get("restored"):
            layout = restored.get("layout", layout)
        live = panel_snapshot(app=self._app)
        focus = focus_profile(self._mode)
        self._emit("workspace_focus_changed", {"mode": self._mode, "workspace_id": self._id})
        self._emit("cognitive_transition_rendered", {"transition": "workspace_open"})
        return {
            "accepted": True,
            "workspace_id": self._id,
            "mode": self._mode,
            "modes": list(WORKSPACE_MODES),
            "layout": layout,
            "live": live,
            "focus": focus,
            "resource_profile": self._profile,
            "supervised": True,
        }

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if mode not in WORKSPACE_MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        layout = build_layout(mode=mode)
        self._layouts.persist(layout)
        routed = route_attention(focus=mode, panels=layout["panels"])
        self._emit("workspace_focus_changed", routed)
        return {"accepted": True, "mode": mode, "layout": layout, "routing": routed}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in RESOURCE_PROFILES:
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        caps = {"ultra_light": 15, "balanced": 30, "immersive": 45, "cinematic": 60}
        return {
            "accepted": True,
            "profile": profile,
            "fps_cap": caps.get(profile, 30),
            "stream_throttle": profile == "ultra_light",
            "lazy_render": True,
        }

    async def quick_command(self, *, query: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_workspace_enabled", False):
            return {"accepted": False, "reason": "cognitive_workspace_disabled"}
        resp = {}
        if hasattr(self._app, "conversational_os"):
            resp = await self._app.conversational_os.interact(text=query)
        return {"accepted": True, "query": query, "response": resp}

    def snapshot(self) -> dict[str, Any]:
        return {
            "workspace_id": self._id,
            "mode": self._mode,
            "profile": self._profile,
            "panels": self._panels,
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_workspace")
''')

w("cognitive_workspace/__init__.py", '''from odin_backend.core.cognitive_workspace.workspace_runtime import CognitiveWorkspaceRuntime
__all__ = ["CognitiveWorkspaceRuntime"]
''')

# --- live_reasoning ---
w("live_reasoning/reasoning_layers.py", '''from __future__ import annotations
from typing import Any


def layer_stack(thought: str) -> list[dict[str, Any]]:
    return [
        {"layer": "perception", "weight": 0.2},
        {"layer": "planning", "weight": 0.5, "text": thought[:80]},
        {"layer": "reflection", "weight": 0.3},
    ]
''')

w("live_reasoning/token_stream_visualizer.py", '''from __future__ import annotations


def tokenize_stream(text: str, *, chunk: int = 8) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + chunk]) for i in range(0, max(len(words), 1), chunk)] or [text]
''')

w("live_reasoning/attention_heatmap.py", '''from __future__ import annotations
from typing import Any


def heatmap(layers: list[dict]) -> dict[str, Any]:
    cells = [round(float(l.get("weight", 0.1)) * 100) for l in layers]
    return {"cells": cells, "max": max(cells) if cells else 0}
''')

w("live_reasoning/live_chain_tracker.py", '''from __future__ import annotations
from typing import Any


class LiveChainTracker:
    def __init__(self) -> None:
        self._chains: list[dict] = []

    def push(self, step: str, *, confidence: float = 0.7) -> dict[str, Any]:
        node = {"step": step, "confidence": confidence}
        self._chains.append(node)
        return node

    def snapshot(self) -> list[dict]:
        return self._chains[-24:]
''')

w("live_reasoning/cognitive_diff.py", '''from __future__ import annotations


def diff_branches(a: str, b: str) -> dict:
    return {"a": a[:120], "b": b[:120], "divergence": a != b}
''')

w("live_reasoning/reasoning_timeline.py", '''from __future__ import annotations
from typing import Any


class ReasoningTimeline:
    def __init__(self) -> None:
        self._events: list[dict] = []

    def record(self, kind: str, payload: dict) -> None:
        self._events.append({"kind": kind, **payload})

    def playback(self, *, limit: int = 20) -> list[dict]:
        return self._events[-limit:]
''')

w("live_reasoning/reasoning_surface.py", '''"""Live streaming reasoning surface (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.live_reasoning.attention_heatmap import heatmap
from odin_backend.core.live_reasoning.cognitive_diff import diff_branches
from odin_backend.core.live_reasoning.live_chain_tracker import LiveChainTracker
from odin_backend.core.live_reasoning.reasoning_layers import layer_stack
from odin_backend.core.live_reasoning.reasoning_timeline import ReasoningTimeline
from odin_backend.core.live_reasoning.token_stream_visualizer import tokenize_stream


class LiveReasoningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._chains = LiveChainTracker()
        self._timeline = ReasoningTimeline()
        self._profile = "balanced"

    async def render(self, *, thought: str = "", branch_b: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "live_reasoning_enabled", False):
            return {"accepted": False, "reason": "live_reasoning_disabled"}
        if hasattr(self._app, "reasoning_streams"):
            await self._app.reasoning_streams.push(thought=thought or "live reasoning")
        layers = layer_stack(thought or "analyzing")
        tokens = tokenize_stream(thought or "…")
        self._chains.push(thought or "step", confidence=0.72)
        hm = heatmap(layers)
        branch = diff_branches(thought, branch_b) if branch_b else None
        self._timeline.record("render", {"tokens": len(tokens)})
        recalls = {}
        if hasattr(self._app, "memory_threads"):
            recalls = await self._app.memory_threads.recall()
        self._emit("reasoning_branch_rendered", {"tokens": len(tokens), "layers": len(layers)})
        caps = {"ultra_light": 15, "balanced": 30, "immersive": 45, "cinematic": 60}
        return {
            "accepted": True,
            "tokens": tokens,
            "layers": layers,
            "heatmap": hm,
            "chain": self._chains.snapshot(),
            "branch_compare": branch,
            "memory_recalls": recalls,
            "hallucination_warning": False,
            "fps_cap": caps.get(self._profile, 30),
            "lazy_render": True,
            "playback": self._timeline.playback(),
        }

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("ultra_light", "balanced", "immersive", "cinematic"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile}

    def snapshot(self) -> dict[str, Any]:
        return {"profile": self._profile, "chain_len": len(self._chains.snapshot())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_reasoning")
''')

w("live_reasoning/__init__.py", '''from odin_backend.core.live_reasoning.reasoning_surface import LiveReasoningRuntime
__all__ = ["LiveReasoningRuntime"]
''')

# --- conversational_presence ---
w("conversational_presence/presence_sessions.py", '''from __future__ import annotations
from typing import Any
from uuid import uuid4


class PresenceSessions:
    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}

    def open(self, *, thread_id: str = "") -> dict[str, Any]:
        sid = thread_id or str(uuid4())
        self._sessions[sid] = {"thread_id": sid, "turns": 0}
        return self._sessions[sid]

    def get(self, sid: str) -> dict | None:
        return self._sessions.get(sid)
''')

w("conversational_presence/conversation_memory_threads.py", '''from __future__ import annotations
from typing import Any


async def recall_thread(app: Any, *, topic: str) -> dict[str, Any]:
    if hasattr(app, "memory_threads"):
        return await app.memory_threads.activate(topic=topic)
    return {"anchors": [topic[:80]]}
''')

w("conversational_presence/realtime_turn_manager.py", '''from __future__ import annotations
from typing import Any


class RealtimeTurnManager:
    def __init__(self) -> None:
        self._turn = 0

    def next_turn(self) -> int:
        self._turn += 1
        return self._turn
''')

w("conversational_presence/interrupt_reasoning.py", '''from __future__ import annotations
from typing import Any


async def handle_interrupt(app: Any, *, reason: str = "operator") -> dict[str, Any]:
    if hasattr(app, "realtime_voice"):
        hit = app.realtime_voice.interrupt()
        return hit if isinstance(hit, dict) else {"interrupted": True, "reason": reason}
    return {"interrupted": True, "reason": reason}
''')

w("conversational_presence/voice_attention.py", '''from __future__ import annotations


def voice_attention(*, energy: float) -> str:
    if energy > 0.8:
        return "focused"
    if energy > 0.4:
        return "engaged"
    return "passive"
''')

w("conversational_presence/emotion_signals.py", '''from __future__ import annotations


def emotion_from_energy(energy: float) -> dict:
    return {"valence": min(1.0, energy), "cadence": "steady" if energy < 0.7 else "animated"}
''')

w("conversational_presence/conversation_continuity.py", '''from __future__ import annotations
from typing import Any


async def restore_context(app: Any) -> dict[str, Any]:
    if hasattr(app, "conversational_os"):
        return await app.conversational_os.restore_thread(thread_id="")
    if hasattr(app, "persistent_cognition"):
        return await app.persistent_cognition.rehydrate_session()
    return {"restored": False}
''')

w("conversational_presence/presence_runtime.py", '''"""Real-time conversational presence layer (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.conversational_presence.conversation_continuity import restore_context
from odin_backend.core.conversational_presence.conversation_memory_threads import recall_thread
from odin_backend.core.conversational_presence.emotion_signals import emotion_from_energy
from odin_backend.core.conversational_presence.interrupt_reasoning import handle_interrupt
from odin_backend.core.conversational_presence.presence_sessions import PresenceSessions
from odin_backend.core.conversational_presence.realtime_turn_manager import RealtimeTurnManager
from odin_backend.core.conversational_presence.voice_attention import voice_attention


class ConversationalPresenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._sessions = PresenceSessions()
        self._turns = RealtimeTurnManager()
        self._familiarity = 0.5

    async def connect(self, *, thread_id: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "conversational_presence_enabled", False):
            return {"accepted": False, "reason": "conversational_presence_disabled"}
        session = self._sessions.open(thread_id=thread_id)
        continuity = await restore_context(self._app)
        self._emit("live_presence_updated", {"session_id": session["thread_id"]})
        return {
            "accepted": True,
            "session": session,
            "continuity": continuity,
            "local_first": True,
            "supervised": True,
        }

    async def turn(self, *, text: str, energy: float = 0.6) -> dict[str, Any]:
        if not getattr(self._app.settings, "conversational_presence_enabled", False):
            return {"accepted": False, "reason": "conversational_presence_disabled"}
        turn = self._turns.next_turn()
        resp = {}
        if hasattr(self._app, "conversational_os"):
            resp = await self._app.conversational_os.interact(text=text)
        recall = await recall_thread(self._app, topic=text[:60])
        self._emit("conversation_memory_recalled", {"turn": turn})
        emotion = emotion_from_energy(energy)
        attention = voice_attention(energy=energy)
        return {
            "accepted": True,
            "turn": turn,
            "response": resp,
            "recall": recall,
            "emotion": emotion,
            "attention": attention,
            "familiarity": self._familiarity,
        }

    async def interrupt(self) -> dict[str, Any]:
        hit = await handle_interrupt(self._app)
        return {"accepted": True, "interrupt": hit}

    def snapshot(self) -> dict[str, Any]:
        return {"familiarity": self._familiarity}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="conversational_presence")
''')

w("conversational_presence/__init__.py", '''from odin_backend.core.conversational_presence.presence_runtime import ConversationalPresenceRuntime
__all__ = ["ConversationalPresenceRuntime"]
''')

# --- evolution_review ---
w("evolution_review/proposal_queue.py", '''from __future__ import annotations
from typing import Any


class ProposalQueue:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def enqueue(self, item: dict) -> dict:
        self._items.append({**item, "status": "pending"})
        return self._items[-1]

    def pending(self) -> list[dict]:
        return [i for i in self._items if i.get("status") == "pending"]
''')

w("evolution_review/upgrade_visualizer.py", '''from __future__ import annotations
from typing import Any


def visualize_upgrade(snapshot: dict) -> dict[str, Any]:
    return {"nodes": list(snapshot.keys())[:8], "approval_required": True}
''')

w("evolution_review/regression_compare.py", '''from __future__ import annotations


def compare(before: dict, after: dict) -> dict:
    return {"delta_keys": list(set(after.keys()) - set(before.keys())), "risk": "medium"}
''')

w("evolution_review/benchmark_diffs.py", '''from __future__ import annotations
from typing import Any


def diff_benchmarks(current: dict, baseline: dict) -> dict[str, Any]:
    return {"current": current, "baseline": baseline, "drift_detected": current != baseline}
''')

w("evolution_review/approval_workflows.py", '''from __future__ import annotations
from typing import Any


def review_action(*, action: str, proposal_id: str) -> dict[str, Any]:
    if action not in ("approve", "reject", "revise"):
        return {"accepted": False, "reason": "invalid_action"}
    return {"accepted": True, "action": action, "proposal_id": proposal_id, "auto_commit": False}
''')

w("evolution_review/rollback_explorer.py", '''from __future__ import annotations
from typing import Any


def simulate_rollback(*, target: str) -> dict[str, Any]:
    return {"target": target, "simulated": True, "main_branch_safe": True}
''')

w("evolution_review/patch_timeline.py", '''from __future__ import annotations
from typing import Any


class PatchTimeline:
    def __init__(self) -> None:
        self._events: list[dict] = []

    def add(self, event: dict) -> None:
        self._events.append(event)

    def history(self) -> list[dict]:
        return self._events[-32:]
''')

w("evolution_review/review_runtime.py", '''"""Supervised evolution review workflow (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.evolution_review.approval_workflows import review_action
from odin_backend.core.evolution_review.benchmark_diffs import diff_benchmarks
from odin_backend.core.evolution_review.patch_timeline import PatchTimeline
from odin_backend.core.evolution_review.proposal_queue import ProposalQueue
from odin_backend.core.evolution_review.regression_compare import compare
from odin_backend.core.evolution_review.rollback_explorer import simulate_rollback
from odin_backend.core.evolution_review.upgrade_visualizer import visualize_upgrade


class EvolutionReviewRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue = ProposalQueue()
        self._timeline = PatchTimeline()

    async def open_review(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "evolution_review_enabled", False):
            return {"accepted": False, "reason": "evolution_review_disabled"}
        review = {}
        if hasattr(self._app, "self_evolution"):
            review["evolution"] = self._app.self_evolution.snapshot()
        if hasattr(self._app, "runtime_benchmarks"):
            review["benchmarks"] = self._app.runtime_benchmarks.snapshot()
        if hasattr(self._app, "autonomous_patching"):
            review["patching"] = self._app.autonomous_patching.snapshot()
        viz = visualize_upgrade(review)
        self._queue.enqueue({"kind": "upgrade", "review": review})
        self._emit("upgrade_review_opened", {"sections": list(review.keys())})
        return {"accepted": True, "review": review, "visual": viz, "approval_required": True}

    async def compare_benchmarks(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "evolution_review_enabled", False):
            return {"accepted": False, "reason": "evolution_review_disabled"}
        current = {}
        baseline = {}
        if hasattr(self._app, "runtime_benchmarks"):
            current = self._app.runtime_benchmarks.snapshot()
        diff = diff_benchmarks(current, baseline)
        return {"accepted": True, "diff": diff}

    async def simulate_rollback(self, *, target: str = "last_stable") -> dict[str, Any]:
        sim = simulate_rollback(target=target)
        self._emit("rollback_simulated", sim)
        self._timeline.add({"kind": "rollback_sim", **sim})
        return {"accepted": True, **sim}

    async def decide(self, *, action: str, proposal_id: str = "latest") -> dict[str, Any]:
        result = review_action(action=action, proposal_id=proposal_id)
        return result

    def snapshot(self) -> dict[str, Any]:
        return {"pending": len(self._queue.pending()), "timeline": self._timeline.history()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="evolution_review")
''')

w("evolution_review/__init__.py", '''from odin_backend.core.evolution_review.review_runtime import EvolutionReviewRuntime
__all__ = ["EvolutionReviewRuntime"]
''')

# --- cognitive_daemon (orchestration layer) ---
w("cognitive_daemon/continuous_attention.py", '''from __future__ import annotations


def heartbeat(*, idle_s: float) -> dict:
    return {"idle_s": idle_s, "attention": "ambient" if idle_s > 120 else "active"}
''')

w("cognitive_daemon/idle_reasoning.py", '''from __future__ import annotations
from typing import Any


async def idle_tick(app: Any) -> dict[str, Any]:
    if hasattr(app, "reasoning_streams"):
        return await app.reasoning_streams.push(thought="idle reflection")
    return {"idle": True}
''')

w("cognitive_daemon/proactive_memory_refresh.py", '''from __future__ import annotations
from typing import Any


async def refresh(app: Any) -> dict[str, Any]:
    if hasattr(app, "memory_threads"):
        return await app.memory_threads.recall()
    return {"refreshed": False}
''')

w("cognitive_daemon/background_reflection.py", '''from __future__ import annotations
from typing import Any


async def reflect(app: Any) -> dict[str, Any]:
    if hasattr(app, "reflection"):
        snap = getattr(app.reflection, "snapshot", lambda: {})()
        return {"reflection": snap}
    return {"reflection": "deferred"}
''')

w("cognitive_daemon/environment_awareness_loop.py", '''from __future__ import annotations
from typing import Any


async def observe(app: Any) -> dict[str, Any]:
    if hasattr(app, "live_environment"):
        return await app.live_environment.update(duration_s=30, reason="daemon_loop")
    return {"observed": False}
''')

w("cognitive_daemon/task_resumption.py", '''from __future__ import annotations
from typing import Any


async def resurface(app: Any) -> dict[str, Any]:
    if hasattr(app, "daily_continuity"):
        return await app.daily_continuity.resume_summary()
    return {"tasks": []}
''')

w("cognitive_daemon/adaptive_focus_scheduler.py", '''from __future__ import annotations

PROFILES = {"ultra_light": 60, "balanced": 30, "immersive": 15, "cinematic": 10}


def tick_interval(profile: str) -> int:
    return PROFILES.get(profile, 30)
''')

w("cognitive_daemon/daemon_orchestrator.py", '''"""Continuous cognitive daemon orchestration (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_daemon.adaptive_focus_scheduler import tick_interval
from odin_backend.core.cognitive_daemon.background_reflection import reflect
from odin_backend.core.cognitive_daemon.continuous_attention import heartbeat
from odin_backend.core.cognitive_daemon.environment_awareness_loop import observe
from odin_backend.core.cognitive_daemon.idle_reasoning import idle_tick
from odin_backend.core.cognitive_daemon.proactive_memory_refresh import refresh
from odin_backend.core.cognitive_daemon.task_resumption import resurface


class CognitiveDaemonOrchestrator:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._profile = "balanced"
        self._idle_s = 0.0

    async def tick(self, *, idle_s: float = 0.0) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_daemon_enabled", False):
            return {"accepted": False, "reason": "cognitive_daemon_disabled"}
        self._idle_s = idle_s
        hb = heartbeat(idle_s=idle_s)
        if hasattr(self._app, "daemon_runtime"):
            await self._app.daemon_runtime.cognitive_tick(wakeword="", energy=0.3)
        idle = await idle_tick(self._app)
        mem = await refresh(self._app)
        ref = await reflect(self._app)
        env = await observe(self._app)
        tasks = await resurface(self._app)
        if tasks.get("unfinished"):
            self._emit("unfinished_task_resurfaced", {"count": len(tasks.get("unfinished", []))})
        self._emit("daemon_attention_shifted", hb)
        return {
            "accepted": True,
            "heartbeat": hb,
            "idle": idle,
            "memory": mem,
            "reflection": ref,
            "environment": env,
            "tasks": tasks,
            "interval_s": tick_interval(self._profile),
            "resource_aware": True,
        }

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("ultra_light", "balanced", "immersive", "cinematic"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile, "interval_s": tick_interval(profile)}

    def snapshot(self) -> dict[str, Any]:
        return {"profile": self._profile, "idle_s": self._idle_s}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_daemon")
''')

w("cognitive_daemon/__init__.py", '''from odin_backend.core.cognitive_daemon.daemon_orchestrator import CognitiveDaemonOrchestrator
__all__ = ["CognitiveDaemonOrchestrator"]
''')

# --- operator_productivity ---
w("operator_productivity/focus_cycles.py", '''from __future__ import annotations
from typing import Any


class FocusCycles:
    def __init__(self) -> None:
        self._cycle_min = 25

    def start(self, *, minutes: int = 25) -> dict[str, Any]:
        self._cycle_min = minutes
        return {"minutes": minutes, "started": True}
''')

w("operator_productivity/session_energy.py", '''from __future__ import annotations


def energy_level(*, focus_minutes: int) -> str:
    if focus_minutes > 90:
        return "low"
    if focus_minutes > 45:
        return "medium"
    return "high"
''')

w("operator_productivity/attention_metrics.py", '''from __future__ import annotations


def score(*, distractions: int, focus_min: int) -> float:
    base = min(1.0, focus_min / 60.0)
    return max(0.0, base - distractions * 0.05)
''')

w("operator_productivity/distraction_detection.py", '''from __future__ import annotations


def detect(*, context_switches: int) -> dict:
    return {"distracted": context_switches > 6, "switches": context_switches}
''')

w("operator_productivity/workflow_optimizer.py", '''from __future__ import annotations
from typing import Any


def optimize(*, bottlenecks: list[str]) -> dict[str, Any]:
    return {"suggestions": bottlenecks[:3], "approval_required": True}
''')

w("operator_productivity/operator_burnout.py", '''from __future__ import annotations


def risk(*, session_hours: float) -> dict:
    return {"burnout_risk": session_hours > 10, "hours": session_hours}
''')

w("operator_productivity/daily_strategy.py", '''from __future__ import annotations
from typing import Any


async def plan(app: Any) -> dict[str, Any]:
    if hasattr(app, "daily_workflow"):
        return await app.daily_workflow.startup_routine()
    return {"plan": "focus engineering block"}
''')

w("operator_productivity/productivity_runtime.py", '''"""Operator productivity orchestrator (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.operator_productivity.attention_metrics import score
from odin_backend.core.operator_productivity.daily_strategy import plan
from odin_backend.core.operator_productivity.distraction_detection import detect
from odin_backend.core.operator_productivity.focus_cycles import FocusCycles
from odin_backend.core.operator_productivity.operator_burnout import risk
from odin_backend.core.operator_productivity.session_energy import energy_level
from odin_backend.core.operator_productivity.workflow_optimizer import optimize


class OperatorProductivityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._cycles = FocusCycles()
        self._focus_min = 0
        self._distractions = 0

    async def start_focus(self, *, minutes: int = 25) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_productivity_enabled", False):
            return {"accepted": False, "reason": "operator_productivity_disabled"}
        cycle = self._cycles.start(minutes=minutes)
        self._focus_min = 0
        return {"accepted": True, "cycle": cycle}

    async def record_distraction(self, *, context_switches: int = 1) -> dict[str, Any]:
        self._distractions += context_switches
        hit = detect(context_switches=self._distractions)
        if hit.get("distracted"):
            self._emit("operator_focus_degraded", hit)
        return {"accepted": True, **hit}

    async def summary(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_productivity_enabled", False):
            return {"accepted": False, "reason": "operator_productivity_disabled"}
        attn = score(distractions=self._distractions, focus_min=self._focus_min)
        energy = energy_level(focus_minutes=self._focus_min)
        strategy = await plan(self._app)
        burnout = risk(session_hours=self._focus_min / 60.0)
        opt = optimize(bottlenecks=["context switching", "long meetings"])
        return {
            "accepted": True,
            "attention_score": attn,
            "energy": energy,
            "strategy": strategy,
            "burnout": burnout,
            "optimizer": opt,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"focus_min": self._focus_min, "distractions": self._distractions}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_productivity")
''')

w("operator_productivity/__init__.py", '''from odin_backend.core.operator_productivity.productivity_runtime import OperatorProductivityRuntime
__all__ = ["OperatorProductivityRuntime"]
''')

print("bootstrap_p46_core complete")

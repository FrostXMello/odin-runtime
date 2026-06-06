"""Bootstrap Prompt 41 core module files."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


# conversation_runtime helpers
w("conversation_runtime/realtime_chat.py", '''"""Streaming chat primitives."""
from __future__ import annotations
from typing import Any

MODES = ("assistant", "engineering", "research", "strategic", "debugging", "copilot", "reflective")

def start_turn(*, mode: str = "assistant", prompt: str = "") -> dict[str, Any]:
    m = mode if mode in MODES else "assistant"
    return {"mode": m, "prompt": prompt[:2000], "streaming": True}
''')

w("conversation_runtime/streaming_dialogue.py", '''"""Token streaming dialogue."""
from __future__ import annotations
from typing import Any

def stream_tokens(text: str, *, chunk: int = 8) -> list[str]:
    return [text[i : i + chunk] for i in range(0, max(len(text), 1), chunk)] or [""]
''')

w("conversation_runtime/contextual_response_engine.py", '''"""Contextual response assembly."""
from __future__ import annotations
from typing import Any

def respond(*, prompt: str, context: dict | None = None) -> dict[str, Any]:
    ctx = context or {}
    return {"text": f"Understood: {prompt[:80]}", "context_keys": list(ctx.keys())[:8], "confidence": 0.72}
''')

w("conversation_runtime/interruption_recovery.py", '''"""Conversation interruption recovery."""
from __future__ import annotations
from typing import Any

def recover(*, partial: str, intent: str = "") -> dict[str, Any]:
    return {"recovered": True, "resume_from": partial[-40:], "intent": intent or "continue"}
''')

w("conversation_runtime/intent_tracker.py", '''"""Multi-turn intent tracking."""
from __future__ import annotations
from typing import Any

def track_intent(*, turns: list[str]) -> dict[str, Any]:
    joined = " ".join(turns[-3:]).lower()
    if "debug" in joined:
        return {"intent": "debugging", "confidence": 0.8}
    if "research" in joined:
        return {"intent": "research", "confidence": 0.75}
    return {"intent": "general", "confidence": 0.6}
''')

w("conversation_runtime/conversation_memory_threads.py", '''"""Persistent conversation threads."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

class ThreadStore:
    def __init__(self) -> None:
        self._threads: dict[str, list[dict]] = {}

    def append(self, thread_id: str, role: str, content: str) -> dict[str, Any]:
        tid = thread_id or str(uuid4())
        self._threads.setdefault(tid, []).append({"role": role, "content": content[:4000]})
        return {"thread_id": tid, "count": len(self._threads[tid])}

    def restore(self, thread_id: str) -> dict[str, Any]:
        msgs = self._threads.get(thread_id, [])
        return {"thread_id": thread_id, "messages": msgs, "restored": bool(msgs)}
''')

w("conversation_runtime/response_personality.py", '''"""Adaptive conversational tone."""
from __future__ import annotations
from typing import Any

def tone_for_mode(mode: str) -> dict[str, Any]:
    tones = {
        "engineering": {"style": "precise", "verbosity": "medium"},
        "debugging": {"style": "diagnostic", "verbosity": "high"},
        "reflective": {"style": "calm", "verbosity": "low"},
    }
    return tones.get(mode, {"style": "helpful", "verbosity": "medium"})
''')

w("conversation_runtime/live_reasoning_renderer.py", '''"""Live reasoning visualization chunks."""
from __future__ import annotations
from typing import Any

def render_reasoning(*, steps: list[str]) -> dict[str, Any]:
    return {"steps": steps[:12], "streaming": True, "complete": len(steps) <= 12}
''')

w("conversation_runtime/conversation_runtime.py", '''"""Real-time conversational runtime orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.conversation_runtime.contextual_response_engine import respond
from odin_backend.core.conversation_runtime.conversation_memory_threads import ThreadStore
from odin_backend.core.conversation_runtime.intent_tracker import track_intent
from odin_backend.core.conversation_runtime.interruption_recovery import recover
from odin_backend.core.conversation_runtime.live_reasoning_renderer import render_reasoning
from odin_backend.core.conversation_runtime.realtime_chat import MODES, start_turn
from odin_backend.core.conversation_runtime.response_personality import tone_for_mode
from odin_backend.core.conversation_runtime.streaming_dialogue import stream_tokens


class ConversationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._threads = ThreadStore()
        self._mode = "assistant"
        self._turns: list[str] = []

    async def chat(self, *, prompt: str, mode: str | None = None, context: dict | None = None, thread_id: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "conversation_runtime_enabled", False):
            return {"accepted": False, "reason": "conversation_runtime_disabled"}
        self._mode = mode or self._mode
        turn = start_turn(mode=self._mode, prompt=prompt)
        if self._mode not in MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        resp = respond(prompt=prompt, context=context)
        if hasattr(self._app, "local_ai"):
            gen = await self._app.local_ai.generate(prompt=prompt, template="summary")
            resp["text"] = gen.get("text", resp["text"])
        tokens = stream_tokens(resp["text"])
        reasoning = render_reasoning(steps=[f"analyze:{prompt[:30]}", "compose response"])
        self._turns.append(prompt)
        intent = track_intent(turns=self._turns)
        thread = self._threads.append(thread_id, "user", prompt)
        self._threads.append(thread["thread_id"], "assistant", resp["text"])
        tone = tone_for_mode(self._mode)
        self._emit("thought_generated", {"mode": self._mode, "tokens": len(tokens)})
        self._emit("reasoning_stream_updated", {"steps": len(reasoning["steps"])})
        return {
            "accepted": True,
            "mode": self._mode,
            "response": resp["text"],
            "tokens": tokens,
            "reasoning": reasoning,
            "intent": intent,
            "tone": tone,
            "thread_id": thread["thread_id"],
            "streaming": True,
        }

    async def restore_thread(self, *, thread_id: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "conversation_runtime_enabled", False):
            return {"accepted": False, "reason": "conversation_runtime_disabled"}
        restored = self._threads.restore(thread_id)
        if restored["restored"]:
            self._emit("conversation_thread_restored", {"thread_id": thread_id, "messages": len(restored["messages"])})
        return {"accepted": True, **restored}

    async def recover_interruption(self, *, partial: str) -> dict[str, Any]:
        rec = recover(partial=partial, intent=self._mode)
        self._emit("reasoning_stream_updated", {"recovered": True})
        return {"accepted": True, **rec}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "turns": len(self._turns), "modes": list(MODES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="conversation_runtime")
''')

w("conversation_runtime/__init__.py", '''from odin_backend.core.conversation_runtime.conversation_runtime import ConversationRuntime
__all__ = ["ConversationRuntime"]
''')

# presence
for name, body in {
"presence/emotion_model.py": '''"""Bounded emotional modeling — simulated, transparent."""
from __future__ import annotations
from typing import Any

def estimate_emotion(*, energy: float, pace: str = "steady") -> dict[str, Any]:
    mood = "neutral"
    if energy > 0.75:
        mood = "focused"
    elif energy < 0.3:
        mood = "calm"
    return {"mood": mood, "energy": round(energy, 3), "simulated": True, "disclosure": "not_consciousness"}
''',
"presence/expression_engine.py": '''"""Visual expression metadata."""
from __future__ import annotations
from typing import Any

def expression_for(mood: str) -> dict[str, Any]:
    palette = {"focused": "#60a5fa", "calm": "#94a3b8", "neutral": "#cbd5e1"}
    return {"color": palette.get(mood, "#cbd5e1"), "animation": "pulse" if mood == "focused" else "idle"}
''',
"presence/interaction_energy.py": '''"""Interaction energy tracking."""
from __future__ import annotations

def track_energy(*, events: int, duration_s: float) -> float:
    rate = events / max(duration_s, 1.0)
    return min(1.0, rate / 5.0)
''',
"presence/operator_sync.py": '''"""Operator synchronization scoring."""
from __future__ import annotations
from typing import Any

def sync_score(*, operator_actions: int, odin_responses: int) -> dict[str, Any]:
    ratio = odin_responses / max(operator_actions, 1)
    return {"score": round(min(1.0, ratio), 3), "balanced": 0.4 <= ratio <= 1.2}
''',
"presence/conversational_rhythm.py": '''"""Conversational pacing."""
from __future__ import annotations

def rhythm(*, wpm: float = 140.0) -> dict[str, float]:
    return {"wpm": wpm, "pause_ms": 250 if wpm > 160 else 400}
''',
"presence/ambient_state.py": '''"""Ambient presence state."""
from __future__ import annotations
from typing import Any

def ambient(*, idle_s: float) -> dict[str, Any]:
    return {"idle": idle_s > 120, "presence": "background" if idle_s > 120 else "active"}
''',
"presence/personality_projection.py": '''"""Personality continuity projection."""
from __future__ import annotations
from typing import Any

TRAITS = ("precise", "supportive", "curious")

def project(*, mode: str = "engineering") -> dict[str, Any]:
    return {"traits": list(TRAITS), "mode": mode, "stable": True}
''',
"presence/embodied_presence.py": '''"""Embodied presence orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.presence.ambient_state import ambient
from odin_backend.core.presence.conversational_rhythm import rhythm
from odin_backend.core.presence.emotion_model import estimate_emotion
from odin_backend.core.presence.expression_engine import expression_for
from odin_backend.core.presence.interaction_energy import track_energy
from odin_backend.core.presence.operator_sync import sync_score
from odin_backend.core.presence.personality_projection import project


class PresenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._events = 0
        self._emotion = estimate_emotion(energy=0.5)
        self._personality = project()

    async def update(self, *, energy: float | None = None, idle_s: float = 0.0) -> dict[str, Any]:
        if not getattr(self._app.settings, "presence_enabled", False):
            return {"accepted": False, "reason": "presence_disabled"}
        e = energy if energy is not None else track_energy(events=self._events, duration_s=max(idle_s, 1))
        self._emotion = estimate_emotion(energy=e)
        expr = expression_for(self._emotion["mood"])
        amb = ambient(idle_s=idle_s)
        sync = sync_score(operator_actions=max(1, self._events), odin_responses=self._events)
        self._emit("presence_shifted", {"mood": self._emotion["mood"], "simulated": True})
        self._emit("emotional_state_updated", {**self._emotion, "expression": expr["color"]})
        return {
            "accepted": True,
            "emotion": self._emotion,
            "expression": expr,
            "ambient": amb,
            "rhythm": rhythm(),
            "sync": sync,
            "personality": self._personality,
            "disclosure": "simulated_emotional_model",
        }

    async def record_interaction(self) -> dict[str, Any]:
        self._events += 1
        return {"accepted": True, "events": self._events}

    def snapshot(self) -> dict[str, Any]:
        return {"emotion": self._emotion, "personality": self._personality, "events": self._events}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="presence")
''',
"presence/__init__.py": '''from odin_backend.core.presence.embodied_presence import PresenceRuntime
__all__ = ["PresenceRuntime"]
''',
}.items():
    w(name, body)

# cognitive_visualization
for name, body in {
"cognitive_visualization/cognition_graph.py": '''from __future__ import annotations
from typing import Any

def build_graph(*, nodes: list[str]) -> dict[str, Any]:
    edges = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
    return {"nodes": nodes, "edges": edges}
''',
"cognitive_visualization/live_reasoning_map.py": '''from __future__ import annotations
from typing import Any

def reasoning_map(*, steps: list[str]) -> dict[str, Any]:
    return {"layers": [{"id": f"s{i}", "label": s} for i, s in enumerate(steps[:10])]}
''',
"cognitive_visualization/thought_stream.py": '''from __future__ import annotations
from typing import Any

class ThoughtStream:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def push(self, text: str, *, kind: str = "thought") -> dict[str, Any]:
        item = {"text": text[:500], "kind": kind}
        self._items.append(item)
        return item

    def snapshot(self) -> list[dict]:
        return self._items[-50:]
''',
"cognitive_visualization/execution_flow_map.py": '''from __future__ import annotations

def flow_map(*, steps: list[str]) -> dict:
    return {"steps": steps, "active": steps[0] if steps else None}
''',
"cognitive_visualization/memory_activity_map.py": '''from __future__ import annotations

def memory_map(*, threads: int) -> dict:
    return {"threads": threads, "active_cells": min(threads, 8)}
''',
"cognitive_visualization/agent_activity_visualizer.py": '''from __future__ import annotations

def agent_graph(*, agents: list[str]) -> dict:
    return {"agents": agents, "links": len(agents)}
''',
"cognitive_visualization/strategy_visualizer.py": '''from __future__ import annotations

def strategy_tree(*, root: str, branches: list[str]) -> dict:
    return {"root": root, "branches": branches[:6]}
''',
"cognitive_visualization/runtime_heatmap.py": '''from __future__ import annotations

def heatmap(*, load: float) -> dict:
    return {"load": round(load, 3), "zones": ["cognition", "memory", "execution"]}
''',
"cognitive_visualization/visualization_runtime.py": '''"""Live cognitive visualization orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_visualization.agent_activity_visualizer import agent_graph
from odin_backend.core.cognitive_visualization.cognition_graph import build_graph
from odin_backend.core.cognitive_visualization.execution_flow_map import flow_map
from odin_backend.core.cognitive_visualization.live_reasoning_map import reasoning_map
from odin_backend.core.cognitive_visualization.memory_activity_map import memory_map
from odin_backend.core.cognitive_visualization.runtime_heatmap import heatmap
from odin_backend.core.cognitive_visualization.strategy_visualizer import strategy_tree
from odin_backend.core.cognitive_visualization.thought_stream import ThoughtStream


class CognitiveVisualizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._stream = ThoughtStream()

    async def render(self, *, thought: str = "", steps: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_visualization_enabled", False):
            return {"accepted": False, "reason": "cognitive_visualization_disabled"}
        steps = steps or ["observe", "reason", "respond"]
        if thought:
            item = self._stream.push(thought)
            self._emit("thought_generated", item)
        graph = build_graph(nodes=steps)
        reasoning = reasoning_map(steps=steps)
        self._emit("reasoning_stream_updated", {"nodes": len(graph["nodes"])})
        return {
            "accepted": True,
            "graph": graph,
            "reasoning_map": reasoning,
            "execution_flow": flow_map(steps=steps),
            "memory_activity": memory_map(threads=3),
            "agents": agent_graph(agents=["planner", "debugger"]),
            "strategy": strategy_tree(root=steps[0], branches=steps[1:]),
            "heatmap": heatmap(load=0.35),
            "thought_stream": self._stream.snapshot(),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"thought_stream": self._stream.snapshot()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_visualization")
''',
"cognitive_visualization/__init__.py": '''from odin_backend.core.cognitive_visualization.visualization_runtime import CognitiveVisualizationRuntime
__all__ = ["CognitiveVisualizationRuntime"]
''',
}.items():
    w(name, body)

# live_overlay
for name, body in {
"live_overlay/contextual_hints.py": '''from __future__ import annotations
from typing import Any

MODES = ("passive", "assistant", "engineering", "debugging", "strategic")

def hint(*, context: dict, mode: str = "assistant") -> dict[str, Any]:
    m = mode if mode in MODES else "assistant"
    return {"text": f"Hint for {context.get('file', 'workspace')}", "mode": m}
''',
"live_overlay/cognitive_notifications.py": '''from __future__ import annotations

def notify(*, title: str, body: str) -> dict:
    return {"title": title[:80], "body": body[:200], "local_only": True}
''',
"live_overlay/inline_reasoning.py": '''from __future__ import annotations

def inline(*, line: int, reasoning: str) -> dict:
    return {"line": line, "reasoning": reasoning[:300]}
''',
"live_overlay/workspace_annotations.py": '''from __future__ import annotations

def annotate(*, target: str, note: str) -> dict:
    return {"target": target, "note": note[:200]}
''',
"live_overlay/debug_overlay.py": '''from __future__ import annotations

def debug_panel(*, error: str) -> dict:
    return {"error": error[:200], "suggestions": ["check imports", "run tests"]}
''',
"live_overlay/execution_overlay.py": '''from __future__ import annotations

def execution_panel(*, workflow_id: str, step: str) -> dict:
    return {"workflow_id": workflow_id, "step": step, "approval_required": True}
''',
"live_overlay/overlay_renderer.py": '''"""Live workspace overlay orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.live_overlay.cognitive_notifications import notify
from odin_backend.core.live_overlay.contextual_hints import MODES, hint
from odin_backend.core.live_overlay.debug_overlay import debug_panel
from odin_backend.core.live_overlay.execution_overlay import execution_panel
from odin_backend.core.live_overlay.inline_reasoning import inline
from odin_backend.core.live_overlay.workspace_annotations import annotate


class LiveOverlayRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "assistant"

    async def render(self, *, context: dict | None = None, mode: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "live_overlay_enabled", False):
            return {"accepted": False, "reason": "live_overlay_disabled"}
        self._mode = mode or self._mode
        ctx = context or {}
        h = hint(context=ctx, mode=self._mode)
        panels = {
            "hint": h,
            "notification": notify(title="Odin", body=h["text"]),
            "inline": inline(line=ctx.get("line", 1), reasoning="contextual analysis"),
            "annotation": annotate(target=ctx.get("file", "workspace"), note=h["text"]),
        }
        if ctx.get("error"):
            panels["debug"] = debug_panel(error=str(ctx["error"]))
        if ctx.get("workflow_id"):
            panels["execution"] = execution_panel(workflow_id=str(ctx["workflow_id"]), step="active")
        self._emit("live_overlay_rendered", {"mode": self._mode, "panels": list(panels.keys())})
        self._emit("attention_focus_changed", {"mode": self._mode})
        return {"accepted": True, "mode": self._mode, "panels": panels, "modes": list(MODES)}

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_overlay")
''',
"live_overlay/__init__.py": '''from odin_backend.core.live_overlay.overlay_renderer import LiveOverlayRuntime
__all__ = ["LiveOverlayRuntime"]
''',
}.items():
    w(name, body)

# self_development
for name, body in {
"self_development/capability_gap_detector.py": '''from __future__ import annotations
from typing import Any

def detect_gaps(*, metrics: dict) -> list[dict[str, Any]]:
    gaps = []
    if metrics.get("latency_ms", 0) > 500:
        gaps.append({"area": "latency", "severity": "medium"})
    if metrics.get("error_rate", 0) > 0.05:
        gaps.append({"area": "reliability", "severity": "high"})
    return gaps
''',
"self_development/learning_opportunity_engine.py": '''from __future__ import annotations

def opportunities(*, gaps: list[dict]) -> list[dict]:
    return [{"title": f"Improve {g['area']}", "priority": g.get("severity", "low")} for g in gaps]
''',
"self_development/architecture_reflection.py": '''from __future__ import annotations

def reflect(*, components: list[str]) -> dict:
    return {"components": components[:10], "observations": ["incremental extension preserved", "supervision intact"]}
''',
"self_development/supervised_evolution.py": '''from __future__ import annotations

def evolve(*, proposal: dict) -> dict:
    return {"accepted": False, "approval_required": True, "proposal": proposal, "direct_modification": False}
''',
"self_development/improvement_queue.py": '''from __future__ import annotations
from typing import Any

class ImprovementQueue:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def enqueue(self, item: dict) -> dict[str, Any]:
        item = {**item, "status": "proposed", "approval_required": True}
        self._items.append(item)
        return item

    def snapshot(self) -> list[dict]:
        return list(self._items)
''',
"self_development/patch_proposal_pipeline.py": '''from __future__ import annotations

def propose_patch(*, title: str, plan: list[str]) -> dict:
    return {"title": title, "plan": plan, "approval_required": True, "auto_apply": False}
''',
"self_development/self_improvement_supervisor.py": '''"""Supervised self-development — proposals only, no direct modification."""
from __future__ import annotations
from typing import Any

from odin_backend.core.self_development.architecture_reflection import reflect
from odin_backend.core.self_development.capability_gap_detector import detect_gaps
from odin_backend.core.self_development.improvement_queue import ImprovementQueue
from odin_backend.core.self_development.learning_opportunity_engine import opportunities
from odin_backend.core.self_development.patch_proposal_pipeline import propose_patch
from odin_backend.core.self_development.supervised_evolution import evolve


class SelfDevelopmentRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue = ImprovementQueue()

    async def analyze(self, *, metrics: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_development_enabled", False):
            return {"accepted": False, "reason": "self_development_disabled"}
        m = metrics or {"latency_ms": 320, "error_rate": 0.01}
        gaps = detect_gaps(metrics=m)
        ops = opportunities(gaps=gaps)
        reflection = reflect(components=["cognitive_shell", "conversation_runtime", "presence"])
        for op in ops:
            item = self._queue.enqueue(op)
            self._emit("improvement_proposed", item)
        self._emit("architecture_reflection_generated", reflection)
        return {
            "accepted": True,
            "gaps": gaps,
            "opportunities": ops,
            "reflection": reflection,
            "approval_required": True,
            "direct_modification": False,
        }

    async def propose(self, *, title: str, plan: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_development_enabled", False):
            return {"accepted": False, "reason": "self_development_disabled"}
        proposal = propose_patch(title=title, plan=plan or ["analyze", "draft patch", "await approval"])
        item = self._queue.enqueue(proposal)
        evo = evolve(proposal=proposal)
        self._emit("improvement_proposed", item)
        return {"accepted": True, "proposal": proposal, "evolution": evo, "approval_required": True}

    def snapshot(self) -> dict[str, Any]:
        return {"queue": self._queue.snapshot(), "direct_modification": False}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="self_development")
''',
"self_development/__init__.py": '''from odin_backend.core.self_development.self_improvement_supervisor import SelfDevelopmentRuntime
__all__ = ["SelfDevelopmentRuntime"]
''',
}.items():
    w(name, body)

# transparency
for name, body in {
"transparency/ai_disclosure.py": '''from __future__ import annotations

def disclosure(*, feature: str) -> dict:
    return {"feature": feature, "ai_generated": True, "local_only": True}
''',
"transparency/cognition_boundaries.py": '''from __future__ import annotations

def boundaries() -> dict:
    return {"autonomy": "supervised", "self_modify": False, "monitoring": "configurable"}
''',
"transparency/operator_visibility.py": '''from __future__ import annotations

def visibility(*, confidence: float, reason: str) -> dict:
    return {"confidence": round(confidence, 3), "reason": reason[:200], "override_allowed": True}
''',
"transparency/autonomy_disclosure.py": '''from __future__ import annotations

def autonomy_status(*, mode: str) -> dict:
    return {"mode": mode, "approval_checkpoints": True, "unrestricted_autonomy": False}
''',
"transparency/transparency_runtime.py": '''"""Safety and transparency layer."""
from __future__ import annotations
from typing import Any

from odin_backend.core.transparency.ai_disclosure import disclosure
from odin_backend.core.transparency.autonomy_disclosure import autonomy_status
from odin_backend.core.transparency.cognition_boundaries import boundaries
from odin_backend.core.transparency.operator_visibility import visibility


class TransparencyRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def explain(self, *, feature: str, confidence: float = 0.7, reason: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "transparency_enabled", False):
            return {"accepted": False, "reason": "transparency_disabled"}
        return {
            "accepted": True,
            "disclosure": disclosure(feature=feature),
            "boundaries": boundaries(),
            "visibility": visibility(confidence=confidence, reason=reason or "heuristic analysis"),
            "autonomy": autonomy_status(mode=getattr(self._app.settings, "survival_mode", "balanced")),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"boundaries": boundaries(), "autonomy": autonomy_status(mode="supervised")}

''',
"transparency/__init__.py": '''from odin_backend.core.transparency.transparency_runtime import TransparencyRuntime
__all__ = ["TransparencyRuntime"]
''',
}.items():
    w(name, body)

# voice extensions
for name, body in {
"realtime_voice/emotional_tts.py": '''from __future__ import annotations

def emotional_tts(*, text: str, mood: str = "neutral") -> dict:
    return {"text": text[:500], "mood": mood, "local_only": True, "simulated_emotion": True}
''',
"realtime_voice/conversational_interrupts.py": '''from __future__ import annotations

def handle_interrupt(*, speaking: bool) -> dict:
    return {"interrupted": speaking, "resume": not speaking}
''',
"realtime_voice/live_transcription_overlay.py": '''from __future__ import annotations

def overlay(*, partial: str) -> dict:
    return {"partial": partial[-120:], "streaming": True}
''',
"realtime_voice/adaptive_voice_profiles.py": '''from __future__ import annotations

PROFILES = ("default", "engineering", "calm", "energetic")

def profile(name: str = "default") -> dict:
    p = name if name in PROFILES else "default"
    return {"profile": p, "wpm": 150 if p == "energetic" else 130}
''',
"realtime_voice/low_latency_streaming.py": '''from __future__ import annotations

def stream_config(*, mode: str = "balanced") -> dict:
    return {"chunk_ms": 40 if mode == "balanced" else 25, "local_only": True}
''',
}.items():
    w(name, body)

print("bootstrap_p41_core complete")

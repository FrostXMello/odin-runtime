"""Bootstrap Prompt 48 persistent cognitive computer modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


PROFILES = ("survival", "lightweight", "balanced", "immersive", "overnight", "cinematic")

# --- cognitive_kernel ---
w("cognitive_kernel/kernel_state.py", '''from __future__ import annotations
import json
import time
from pathlib import Path


def save_state(*, path: str, state: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({**state, "saved_at": time.time()}), encoding="utf-8")
    return {"saved": True}


def load_state(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "state": json.loads(p.read_text(encoding="utf-8"))}
''')

w("cognitive_kernel/persistent_attention.py", '''from __future__ import annotations


def attention_vector(*, focus: str, weight: float = 0.7) -> dict:
    return {"focus": focus[:120], "weight": weight}
''')

w("cognitive_kernel/reasoning_scheduler.py", '''from __future__ import annotations

INTERVALS = {"survival": 120, "lightweight": 60, "balanced": 30, "immersive": 15, "overnight": 90, "cinematic": 10}


def schedule(profile: str) -> int:
    return INTERVALS.get(profile, 30)
''')

w("cognitive_kernel/continuity_engine.py", '''from __future__ import annotations
from typing import Any


async def rehydrate(app: Any) -> dict:
    out = {}
    if hasattr(app, "persistent_cognition"):
        out["cognition"] = await app.persistent_cognition.rehydrate_session()
    if hasattr(app, "project_memory"):
        out["project"] = await app.project_memory.resume()
    return out
''')

w("cognitive_kernel/operator_state.py", '''from __future__ import annotations


class OperatorState:
    def __init__(self) -> None:
        self._focus = "workspace"
        self._sessions = 0

    def shift(self, focus: str) -> dict:
        self._focus = focus[:80]
        self._sessions += 1
        return {"focus": self._focus, "sessions": self._sessions}
''')

w("cognitive_kernel/context_prioritizer.py", '''from __future__ import annotations
from typing import Any


def prioritize(*, contexts: list[dict]) -> list[dict]:
    return sorted(contexts, key=lambda c: c.get("weight", 0), reverse=True)[:8]
''')

w("cognitive_kernel/kernel_metrics.py", '''from __future__ import annotations


def metrics(*, ticks: int, memory_links: int) -> dict:
    return {"ticks": ticks, "memory_links": memory_links, "healthy": True}
''')

w("cognitive_kernel/cognitive_kernel.py", '''"""Persistent cognitive kernel orchestrator (Prompt 48)."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

from odin_backend.core.cognitive_kernel.continuity_engine import rehydrate
from odin_backend.core.cognitive_kernel.context_prioritizer import prioritize
from odin_backend.core.cognitive_kernel.kernel_metrics import metrics
from odin_backend.core.cognitive_kernel.kernel_state import load_state, save_state
from odin_backend.core.cognitive_kernel.operator_state import OperatorState
from odin_backend.core.cognitive_kernel.persistent_attention import attention_vector
from odin_backend.core.cognitive_kernel.reasoning_scheduler import schedule

PROFILES = ("survival", "lightweight", "balanced", "immersive", "overnight", "cinematic")


class CognitiveKernelRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._id = str(uuid4())
        self._profile = "balanced"
        self._ticks = 0
        self._operator = OperatorState()
        self._path = "./data/cognitive_kernel.json"

    async def heartbeat(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_kernel_enabled", False):
            return {"accepted": False, "reason": "cognitive_kernel_disabled"}
        self._ticks += 1
        attn = attention_vector(focus=self._operator._focus)
        if hasattr(self._app, "cognitive_daemon"):
            await self._app.cognitive_daemon.tick(idle_s=0)
        self._emit("kernel_attention_shifted", attn)
        caps = {"survival": 10, "lightweight": 15, "balanced": 30, "immersive": 45, "overnight": 8, "cinematic": 60}
        return {
            "accepted": True,
            "kernel_id": self._id,
            "tick": self._ticks,
            "attention": attn,
            "interval_s": schedule(self._profile),
            "metrics": metrics(ticks=self._ticks, memory_links=0),
            "fps_cap": caps.get(self._profile, 30),
            "orchestration_layer": True,
        }

    async def prioritize_context(self, *, contexts: list[dict] | None = None) -> dict[str, Any]:
        ctx = prioritize(contexts=contexts or [{"weight": 0.5, "source": "workspace"}])
        return {"accepted": True, "contexts": ctx}

    async def restore(self) -> dict[str, Any]:
        restored = load_state(path=self._path)
        continuity = await rehydrate(self._app)
        if restored.get("restored"):
            self._emit("cross_runtime_sync_completed", {"kernel_id": self._id})
        return {"accepted": True, "kernel": restored, "continuity": continuity}

    async def focus(self, *, focus: str) -> dict[str, Any]:
        hit = self._operator.shift(focus)
        self._emit("kernel_attention_shifted", hit)
        return {"accepted": True, **hit}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in PROFILES:
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        save_state(path=self._path, state={"profile": profile, "kernel_id": self._id})
        return {"accepted": True, "profile": profile, "pause_heavy": profile == "survival"}

    def snapshot(self) -> dict[str, Any]:
        return {"kernel_id": self._id, "profile": self._profile, "ticks": self._ticks}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_kernel")
''')

w("cognitive_kernel/__init__.py", '''from odin_backend.core.cognitive_kernel.cognitive_kernel import CognitiveKernelRuntime
__all__ = ["CognitiveKernelRuntime"]
''')

# --- memory_fabric ---
w("memory_fabric/episodic_threads.py", '''from __future__ import annotations


class EpisodicThreads:
    def __init__(self) -> None:
        self._threads: list[dict] = []

    def add(self, topic: str) -> dict:
        t = {"topic": topic[:80]}
        self._threads.append(t)
        return t
''')

w("memory_fabric/cross_runtime_memory.py", '''from __future__ import annotations
from typing import Any


async def link_runtimes(app: Any) -> dict:
    links = []
    if hasattr(app, "memory_threads"):
        links.append("memory_threads")
    if hasattr(app, "project_memory"):
        links.append("project_memory")
    return {"links": links}
''')

w("memory_fabric/temporal_linking.py", '''from __future__ import annotations


def link_events(events: list[str]) -> list[dict]:
    return [{"a": events[i], "b": events[i + 1]} for i in range(max(0, len(events) - 1))]
''')

w("memory_fabric/semantic_continuity.py", '''from __future__ import annotations


def stitch(*, prior: str, current: str) -> dict:
    return {"prior": prior[:60], "current": current[:60], "continuous": True}
''')

w("memory_fabric/attention_index.py", '''from __future__ import annotations


def index(items: list[str], *, weight: float = 0.5) -> list[dict]:
    return [{"item": i[:60], "weight": weight} for i in items[:12]]
''')

w("memory_fabric/memory_rehydration.py", '''from __future__ import annotations
import json
from pathlib import Path


def rehydrate(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "graph": json.loads(p.read_text(encoding="utf-8"))}
''')

w("memory_fabric/relevance_decay.py", '''from __future__ import annotations


def decay(*, age_hours: float) -> float:
    return max(0.1, 1.0 - age_hours / 168.0)
''')

w("memory_fabric/memory_fabric.py", '''"""Unified memory fabric (Prompt 48)."""
from __future__ import annotations
from typing import Any
import json
from pathlib import Path

from odin_backend.core.memory_fabric.attention_index import index
from odin_backend.core.memory_fabric.cross_runtime_memory import link_runtimes
from odin_backend.core.memory_fabric.episodic_threads import EpisodicThreads
from odin_backend.core.memory_fabric.memory_rehydration import rehydrate
from odin_backend.core.memory_fabric.relevance_decay import decay
from odin_backend.core.memory_fabric.semantic_continuity import stitch
from odin_backend.core.memory_fabric.temporal_linking import link_events


class MemoryFabricRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._threads = EpisodicThreads()
        self._path = "./data/memory_fabric.json"

    async def link(self, *, topic: str, prior: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "memory_fabric_enabled", False):
            return {"accepted": False, "reason": "memory_fabric_disabled"}
        thread = self._threads.add(topic)
        links = await link_runtimes(self._app)
        cont = stitch(prior=prior, current=topic) if prior else {}
        temporal = link_events([prior, topic] if prior else [topic])
        self._emit("memory_fabric_linked", {"topic": topic[:40], "links": links.get("links", [])})
        graph = {"threads": [thread], "temporal": temporal, "continuity": cont}
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        Path(self._path).write_text(json.dumps(graph), encoding="utf-8")
        return {"accepted": True, "thread": thread, "links": links, "graph": graph}

    async def recall(self, *, query: str = "") -> dict[str, Any]:
        restored = rehydrate(path=self._path)
        items = index([query] if query else ["session"], weight=decay(age_hours=1))
        if hasattr(self._app, "memory_threads"):
            await self._app.memory_threads.recall()
        return {"accepted": True, "restored": restored, "attention_index": items}

    def snapshot(self) -> dict[str, Any]:
        return {"threads": len(self._threads._threads)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="memory_fabric")
''')

w("memory_fabric/__init__.py", '''from odin_backend.core.memory_fabric.memory_fabric import MemoryFabricRuntime
__all__ = ["MemoryFabricRuntime"]
''')

# --- environment_intelligence ---
w("environment_intelligence/workspace_understanding.py", '''from __future__ import annotations


def understand(*, repo: str, file: str = "") -> dict:
    return {"repo": repo, "file": file, "intent": "engineering" if file else "explore"}
''')

w("environment_intelligence/attention_tracking.py", '''from __future__ import annotations


def track(*, focus: str) -> dict:
    return {"focus": focus[:80], "intensity": 0.7}
''')

w("environment_intelligence/operator_patterns.py", '''from __future__ import annotations


def patterns(*, switches: int) -> dict:
    return {"context_switches": switches, "deep_work": switches < 4}
''')

w("environment_intelligence/window_semantics.py", '''from __future__ import annotations


def semantics(*, title: str, app: str) -> dict:
    return {"title": title[:80], "app": app[:40], "coding": "code" in title.lower()}
''')

w("environment_intelligence/workflow_prediction.py", '''from __future__ import annotations


def predict(*, intent: str) -> dict:
    return {"next_action": f"continue {intent[:40]}", "confidence": 0.65}
''')

w("environment_intelligence/context_classifier.py", '''from __future__ import annotations


def classify(*, context: str) -> str:
    c = context.lower()
    if "debug" in c:
        return "debugging"
    if "test" in c:
        return "testing"
    return "engineering"
''')

w("environment_intelligence/environment_memory.py", '''from __future__ import annotations


class EnvironmentMemory:
    def __init__(self) -> None:
        self._entries: list[dict] = []

    def remember(self, entry: dict) -> None:
        self._entries.append(entry)

    def recent(self) -> list[dict]:
        return self._entries[-16:]
''')

w("environment_intelligence/environment_runtime.py", '''"""Live environment intelligence (Prompt 48)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.environment_intelligence.attention_tracking import track
from odin_backend.core.environment_intelligence.context_classifier import classify
from odin_backend.core.environment_intelligence.environment_memory import EnvironmentMemory
from odin_backend.core.environment_intelligence.operator_patterns import patterns
from odin_backend.core.environment_intelligence.window_semantics import semantics
from odin_backend.core.environment_intelligence.workflow_prediction import predict
from odin_backend.core.environment_intelligence.workspace_understanding import understand


class EnvironmentIntelligenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._memory = EnvironmentMemory()

    async def observe(self, *, repo: str = "", file: str = "", title: str = "", app_name: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "environment_intelligence_enabled", False):
            return {"accepted": False, "reason": "environment_intelligence_disabled"}
        ws = understand(repo=repo or "local", file=file)
        win = semantics(title=title, app=app_name or "editor")
        attn = track(focus=file or repo)
        pred = predict(intent=ws.get("intent", "work"))
        kind = classify(context=file or repo)
        entry = {"ws": ws, "window": win, "prediction": pred}
        self._memory.remember(entry)
        self._emit("environment_context_detected", {"kind": kind, "repo": repo})
        self._emit("workflow_prediction_generated", pred)
        if hasattr(self._app, "live_environment"):
            await self._app.live_environment.update(duration_s=60, reason=kind)
        return {
            "accepted": True,
            "understanding": ws,
            "attention": attn,
            "patterns": patterns(switches=2),
            "prediction": pred,
            "memory": self._memory.recent(),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"entries": len(self._memory.recent())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="environment_intelligence")
''')

w("environment_intelligence/__init__.py", '''from odin_backend.core.environment_intelligence.environment_runtime import EnvironmentIntelligenceRuntime
__all__ = ["EnvironmentIntelligenceRuntime"]
''')

# --- cognitive_streams ---
w("cognitive_streams/stream_compression.py", '''from __future__ import annotations


def compress(thoughts: list[str], *, max_items: int = 8) -> list[str]:
    return thoughts[-max_items:]
''')

w("cognitive_streams/attention_streams.py", '''from __future__ import annotations


def stream(*, focus: str) -> dict:
    return {"channel": "attention", "focus": focus[:60]}
''')

w("cognitive_streams/reasoning_snapshots.py", '''from __future__ import annotations


class ReasoningSnapshots:
    def __init__(self) -> None:
        self._snaps: list[dict] = []

    def capture(self, thought: str) -> dict:
        s = {"thought": thought[:120]}
        self._snaps.append(s)
        return s
''')

w("cognitive_streams/reflection_streams.py", '''from __future__ import annotations


def reflect(*, summary: str) -> dict:
    return {"reflection": summary[:160]}
''')

w("cognitive_streams/live_memory_streams.py", '''from __future__ import annotations


def replay(items: list[str]) -> list[dict]:
    return [{"item": i[:60]} for i in items[-6:]]
''')

w("cognitive_streams/contextual_stream_router.py", '''from __future__ import annotations


def route(*, profile: str) -> list[str]:
    if profile in ("survival", "lightweight"):
        return ["kernel:runtime"]
    return ["kernel:runtime", "cognitive-streams:runtime", "memory-fabric:runtime"]
''')

w("cognitive_streams/thought_stream_runtime.py", '''"""Realtime cognitive streams (Prompt 48)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_streams.attention_streams import stream as attention_stream
from odin_backend.core.cognitive_streams.contextual_stream_router import route
from odin_backend.core.cognitive_streams.live_memory_streams import replay
from odin_backend.core.cognitive_streams.reasoning_snapshots import ReasoningSnapshots
from odin_backend.core.cognitive_streams.reflection_streams import reflect
from odin_backend.core.cognitive_streams.stream_compression import compress


class CognitiveStreamsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._thoughts: list[str] = []
        self._snaps = ReasoningSnapshots()
        self._profile = "balanced"

    async def push(self, *, thought: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_streams_enabled", False):
            return {"accepted": False, "reason": "cognitive_streams_disabled"}
        self._thoughts.append(thought[:200])
        compressed = compress(self._thoughts)
        if len(compressed) < len(self._thoughts):
            self._emit("thought_stream_compressed", {"before": len(self._thoughts), "after": len(compressed)})
        snap = self._snaps.capture(thought)
        if hasattr(self._app, "reasoning_streams"):
            await self._app.reasoning_streams.push(thought=thought)
        return {
            "accepted": True,
            "stream": compressed,
            "snapshot": snap,
            "attention": attention_stream(focus=thought),
            "channels": route(profile=self._profile),
            "low_resource": self._profile in ("survival", "lightweight"),
        }

    async def reflect_stream(self, *, summary: str) -> dict[str, Any]:
        r = reflect(summary=summary)
        mem = replay(self._thoughts)
        return {"accepted": True, "reflection": r, "memory_replay": mem}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("survival", "lightweight", "balanced", "immersive", "overnight", "cinematic"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile}

    def snapshot(self) -> dict[str, Any]:
        return {"thoughts": len(self._thoughts)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_streams")
''')

w("cognitive_streams/__init__.py", '''from odin_backend.core.cognitive_streams.thought_stream_runtime import CognitiveStreamsRuntime
__all__ = ["CognitiveStreamsRuntime"]
''')

# --- personal_presence ---
w("personal_presence/presence_continuity.py", '''from __future__ import annotations
from typing import Any


async def restore(app: Any) -> dict:
    if hasattr(app, "conversational_presence"):
        return await app.conversational_presence.connect()
    return {"restored": False}
''')

w("personal_presence/operator_relationship_memory.py", '''from __future__ import annotations


class RelationshipMemory:
    def __init__(self) -> None:
        self._interactions = 0

    def interact(self) -> dict:
        self._interactions += 1
        return {"interactions": self._interactions}
''')

w("personal_presence/adaptive_personality.py", '''from __future__ import annotations


def refine(*, familiarity: float) -> dict:
    return {"tone": "supportive", "familiarity": familiarity, "deceptive_consciousness": False}
''')

w("personal_presence/interaction_rhythm.py", '''from __future__ import annotations


def rhythm(*, energy: float) -> str:
    return "steady" if energy < 0.7 else "animated"
''')

w("personal_presence/conversation_identity.py", '''from __future__ import annotations
from uuid import uuid4


def identity() -> dict:
    return {"assistant": "Odin", "simulated_emotion_disclosure": True, "identity_id": str(uuid4())}
''')

w("personal_presence/session_familiarity.py", '''from __future__ import annotations


def score(*, sessions: int) -> float:
    return min(1.0, sessions / 50.0)
''')

w("personal_presence/presence_state.py", '''from __future__ import annotations
from typing import Any

from odin_backend.core.personal_presence.adaptive_personality import refine
from odin_backend.core.personal_presence.conversation_identity import identity
from odin_backend.core.personal_presence.interaction_rhythm import rhythm
from odin_backend.core.personal_presence.operator_relationship_memory import RelationshipMemory
from odin_backend.core.personal_presence.presence_continuity import restore
from odin_backend.core.personal_presence.session_familiarity import score


class PersonalPresenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._relationship = RelationshipMemory()
        self._sessions = 0
        self._familiarity = 0.3

    async def connect(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "personal_presence_enabled", False):
            return {"accepted": False, "reason": "personal_presence_disabled"}
        self._sessions += 1
        rel = self._relationship.interact()
        self._familiarity = score(sessions=self._sessions)
        cont = await restore(self._app)
        ident = identity()
        pers = refine(familiarity=self._familiarity)
        self._emit("presence_familiarity_updated", {"familiarity": self._familiarity})
        return {
            "accepted": True,
            "identity": ident,
            "personality": pers,
            "continuity": cont,
            "relationship": rel,
            "bounded_personality": True,
            "local_first": True,
        }

    async def interact(self, *, text: str, energy: float = 0.6) -> dict[str, Any]:
        self._relationship.interact()
        cadence = rhythm(energy=energy)
        return {"accepted": True, "cadence": cadence, "familiarity": self._familiarity, "text_len": len(text)}

    def snapshot(self) -> dict[str, Any]:
        return {"familiarity": self._familiarity, "sessions": self._sessions}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="personal_presence")
''')

w("personal_presence/__init__.py", '''from odin_backend.core.personal_presence.presence_state import PersonalPresenceRuntime
__all__ = ["PersonalPresenceRuntime"]
''')

# --- proactive_assistance ---
w("proactive_assistance/interruption_scoring.py", '''from __future__ import annotations


def score(*, urgency: float, operator_busy: bool) -> float:
    if operator_busy:
        return urgency * 0.3
    return urgency
''')

w("proactive_assistance/timing_prediction.py", '''from __future__ import annotations


def predict_idle(*, idle_s: float) -> bool:
    return idle_s > 45
''')

w("proactive_assistance/workflow_assistance.py", '''from __future__ import annotations


def hint(*, workflow: str) -> dict:
    return {"hint": f"Consider reviewing {workflow[:40]}", "non_invasive": True}
''')

w("proactive_assistance/attention_intervention.py", '''from __future__ import annotations


def safe_intervene(*, score: float) -> bool:
    return score > 0.55
''')

w("proactive_assistance/contextual_assistance.py", '''from __future__ import annotations
from typing import Any


async def contextualize(app: Any, *, context: str) -> dict:
    if hasattr(app, "daily_continuity"):
        return await app.daily_continuity.resume_summary()
    return {"context": context[:80]}
''')

w("proactive_assistance/suggestion_priority.py", '''from __future__ import annotations


def prioritize(suggestions: list[dict]) -> list[dict]:
    return sorted(suggestions, key=lambda s: s.get("priority", 0), reverse=True)[:5]
''')

w("proactive_assistance/assistance_engine.py", '''"""Proactive assistance runtime (Prompt 48)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.proactive_assistance.attention_intervention import safe_intervene
from odin_backend.core.proactive_assistance.contextual_assistance import contextualize
from odin_backend.core.proactive_assistance.interruption_scoring import score
from odin_backend.core.proactive_assistance.suggestion_priority import prioritize
from odin_backend.core.proactive_assistance.timing_prediction import predict_idle
from odin_backend.core.proactive_assistance.workflow_assistance import hint


class ProactiveAssistanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def evaluate(self, *, context: str = "", idle_s: float = 0.0, urgency: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "proactive_assistance_runtime_enabled", False):
            return {"accepted": False, "reason": "proactive_assistance_runtime_disabled"}
        s = score(urgency=urgency, operator_busy=idle_s < 10)
        if not safe_intervene(score=s):
            return {"accepted": True, "intervention": False, "reason": "attention_safe_hold"}
        if not predict_idle(idle_s=idle_s) and urgency < 0.8:
            return {"accepted": True, "intervention": False, "reason": "not_idle"}
        h = hint(workflow=context or "engineering")
        ctx = await contextualize(self._app, context=context)
        suggestions = prioritize([{"priority": s, **h}])
        self._emit("assistance_intervention_generated", {"count": len(suggestions)})
        return {
            "accepted": True,
            "intervention": True,
            "suggestions": suggestions,
            "context": ctx,
            "operator_controlled": True,
            "non_invasive": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="proactive_assistance")
''')

w("proactive_assistance/__init__.py", '''from odin_backend.core.proactive_assistance.assistance_engine import ProactiveAssistanceRuntime
__all__ = ["ProactiveAssistanceRuntime"]
''')

# --- cognitive_orchestration ---
w("cognitive_orchestration/cognition_tick_engine.py", '''from __future__ import annotations
from typing import Any


async def tick(app: Any) -> dict:
    results = {}
    if hasattr(app, "cognitive_kernel"):
        results["kernel"] = await app.cognitive_kernel.heartbeat()
    return results
''')

w("cognitive_orchestration/runtime_attention_loop.py", '''from __future__ import annotations


def loop(*, profile: str) -> dict:
    return {"profile": profile, "interval_s": 30 if profile == "balanced" else 60}
''')

w("cognitive_orchestration/background_reflection_scheduler.py", '''from __future__ import annotations
from typing import Any


async def reflect(app: Any) -> dict:
    if hasattr(app, "cognitive_streams"):
        return await app.cognitive_streams.reflect_stream(summary="background reflection")
    return {"reflection": "deferred"}
''')

w("cognitive_orchestration/deferred_reasoning_queue.py", '''from __future__ import annotations


class DeferredReasoningQueue:
    def __init__(self) -> None:
        self._queue: list[str] = []

    def defer(self, thought: str) -> None:
        self._queue.append(thought[:120])

    def drain(self, limit: int = 4) -> list[str]:
        out = self._queue[:limit]
        self._queue = self._queue[limit:]
        return out
''')

w("cognitive_orchestration/cross_runtime_synchronizer.py", '''from __future__ import annotations
from typing import Any


async def sync(app: Any) -> dict:
    synced = []
    for name in ("cognitive_workspace", "memory_fabric", "cognitive_daemon"):
        if hasattr(app, name):
            synced.append(name)
    return {"synced": synced}
''')

w("cognitive_orchestration/resource_balancer.py", '''from __future__ import annotations

CAPS = {"survival": 8, "lightweight": 15, "balanced": 30, "immersive": 45, "overnight": 6, "cinematic": 60}


def balance(profile: str) -> dict:
    return {"fps_cap": CAPS.get(profile, 30), "agent_limit": 2 if profile in ("survival", "lightweight") else 4}
''')

w("cognitive_orchestration/overnight_cognition.py", '''from __future__ import annotations
from typing import Any


async def overnight(app: Any) -> dict:
    if hasattr(app, "continuous_engineering"):
        return await app.continuous_engineering.overnight()
    return {"analysis": "lightweight overnight scan"}
''')

w("cognitive_orchestration/orchestration_runtime.py", '''"""Cognitive orchestration daemon (Prompt 48)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_orchestration.background_reflection_scheduler import reflect
from odin_backend.core.cognitive_orchestration.cognition_tick_engine import tick
from odin_backend.core.cognitive_orchestration.cross_runtime_synchronizer import sync
from odin_backend.core.cognitive_orchestration.deferred_reasoning_queue import DeferredReasoningQueue
from odin_backend.core.cognitive_orchestration.overnight_cognition import overnight
from odin_backend.core.cognitive_orchestration.resource_balancer import balance
from odin_backend.core.cognitive_orchestration.runtime_attention_loop import loop


class CognitiveOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue = DeferredReasoningQueue()
        self._profile = "balanced"

    async def cognition_tick(self, *, idle_s: float = 0.0) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_orchestration_enabled", False):
            return {"accepted": False, "reason": "cognitive_orchestration_disabled"}
        t = await tick(self._app)
        bal = balance(self._profile)
        attn = loop(profile=self._profile)
        deferred = self._queue.drain()
        synced = await sync(self._app)
        self._emit("cognitive_tick_executed", {"idle_s": idle_s})
        self._emit("cross_runtime_sync_completed", synced)
        return {
            "accepted": True,
            "tick": t,
            "balance": bal,
            "attention_loop": attn,
            "deferred": deferred,
            "sync": synced,
            "resource_aware": True,
        }

    async def overnight_cycle(self) -> dict[str, Any]:
        result = await overnight(self._app)
        ref = await reflect(self._app)
        self._emit("overnight_reflection_completed", {"completed": True})
        return {"accepted": True, "overnight": result, "reflection": ref}

    async def defer(self, *, thought: str) -> dict[str, Any]:
        self._queue.defer(thought)
        return {"accepted": True, "queued": True}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("survival", "lightweight", "balanced", "immersive", "overnight", "cinematic"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile, **balance(profile)}

    def snapshot(self) -> dict[str, Any]:
        return {"profile": self._profile}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_orchestration")
''')

w("cognitive_orchestration/__init__.py", '''from odin_backend.core.cognitive_orchestration.orchestration_runtime import CognitiveOrchestrationRuntime
__all__ = ["CognitiveOrchestrationRuntime"]
''')

print("bootstrap_p48_core complete")

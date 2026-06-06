"""Bootstrap Prompt 49 adaptive autonomous cognitive OS modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


PROFILES = ("survival", "balanced", "immersive", "cinematic", "overnight_autonomous")

# --- adaptive_runtime ---
w("adaptive_runtime/runtime_priority_engine.py", '''from __future__ import annotations


def prioritize(*, load: float) -> str:
    if load > 0.8:
        return "reasoning"
    if load > 0.5:
        return "engineering"
    return "workspace"
''')

w("adaptive_runtime/dynamic_attention_router.py", '''from __future__ import annotations


def route(*, focus: str) -> dict:
    return {"primary": focus[:60], "secondary": "background"}
''')

w("adaptive_runtime/cognitive_load_balancer.py", '''"""Cognitive load balancer (Prompt 49)."""
from __future__ import annotations
from typing import Any


class CognitiveLoadBalancer:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._load = 0.4

    async def balance(self, *, load: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_load_balancing_enabled", False):
            return {"accepted": False, "reason": "cognitive_load_balancing_disabled"}
        self._load = min(1.0, max(0.0, load))
        throttle = self._load > 0.75
        self._emit("cognition_load_balanced", {"load": self._load, "throttle": throttle})
        return {
            "accepted": True,
            "load": self._load,
            "throttle_streams": throttle,
            "agent_limit": 2 if throttle else 4,
            "lazy_render": throttle,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"load": self._load}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_load_balancer")
''')

w("adaptive_runtime/background_optimization_loop.py", '''from __future__ import annotations
from typing import Any


async def optimize(app: Any) -> dict:
    if hasattr(app, "cognitive_orchestration"):
        return await app.cognitive_orchestration.cognition_tick(idle_s=120)
    return {"optimized": True}
''')

w("adaptive_runtime/cognitive_state_controller.py", '''from __future__ import annotations

INTENSITY = {"survival": 0.2, "balanced": 0.5, "immersive": 0.8, "cinematic": 0.9, "overnight_autonomous": 0.15}


def intensity(profile: str) -> float:
    return INTENSITY.get(profile, 0.5)
''')

w("adaptive_runtime/adaptive_runtime_manager.py", '''"""Adaptive cognitive runtime manager (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.adaptive_runtime.background_optimization_loop import optimize
from odin_backend.core.adaptive_runtime.cognitive_state_controller import intensity
from odin_backend.core.adaptive_runtime.dynamic_attention_router import route
from odin_backend.core.adaptive_runtime.runtime_priority_engine import prioritize


class AdaptiveRuntimeManager:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._profile = "balanced"

    async def scale(self, *, load: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "adaptive_runtime_enabled", False):
            return {"accepted": False, "reason": "adaptive_runtime_disabled"}
        bal = {}
        if hasattr(self._app, "cognitive_load_balancer"):
            bal = await self._app.cognitive_load_balancer.balance(load=load)
        priority = prioritize(load=load)
        attn = route(focus=priority)
        inten = intensity(self._profile)
        self._emit("adaptive_scaling_applied", {"profile": self._profile, "intensity": inten})
        self._emit("runtime_priority_shifted", {"priority": priority})
        caps = {"survival": 10, "balanced": 30, "immersive": 45, "cinematic": 60, "overnight_autonomous": 8}
        return {
            "accepted": True,
            "profile": self._profile,
            "intensity": inten,
            "priority": priority,
            "routing": attn,
            "balance": bal,
            "fps_cap": caps.get(self._profile, 30),
        }

    async def optimize_background(self) -> dict[str, Any]:
        result = await optimize(self._app)
        self._emit("background_optimization_completed", {"completed": True})
        return {"accepted": True, "optimization": result}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("survival", "balanced", "immersive", "cinematic", "overnight_autonomous"):
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile}

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="adaptive_runtime")
''')

w("adaptive_runtime/__init__.py", '''from odin_backend.core.adaptive_runtime.adaptive_runtime_manager import AdaptiveRuntimeManager
from odin_backend.core.adaptive_runtime.cognitive_load_balancer import CognitiveLoadBalancer
__all__ = ["AdaptiveRuntimeManager", "CognitiveLoadBalancer"]
''')

# --- autonomous_workspace ---
w("autonomous_workspace/workspace_continuity_v2.py", '''from __future__ import annotations
import json
from pathlib import Path


def save_graph(*, path: str, graph: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(graph), encoding="utf-8")
    return {"saved": True}


def load_graph(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "graph": json.loads(p.read_text(encoding="utf-8"))}
''')

w("autonomous_workspace/session_prediction_engine.py", '''from __future__ import annotations


def predict(*, history: list[str]) -> dict:
    nxt = history[-1] if history else "resume engineering"
    return {"next_task": nxt, "confidence": 0.62}
''')

w("autonomous_workspace/workflow_recovery_system.py", '''from __future__ import annotations
from typing import Any


async def recover(app: Any) -> dict:
    if hasattr(app, "daily_continuity"):
        return await app.daily_continuity.resume_summary()
    return {"workflows": []}
''')

w("autonomous_workspace/intent_continuation_runtime.py", '''from __future__ import annotations


def continue_intent(*, intent: str) -> dict:
    return {"intent": intent[:120], "continued": True}
''')

w("autonomous_workspace/daily_resumption_planner.py", '''from __future__ import annotations
from typing import Any


async def plan(app: Any) -> dict:
    if hasattr(app, "daily_operator_experience"):
        return await app.daily_operator_experience.startup()
    return {"plan": "focus block"}
''')

w("autonomous_workspace/autonomous_workspace_runtime.py", '''"""Persistent autonomous workspace (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.autonomous_workspace.daily_resumption_planner import plan
from odin_backend.core.autonomous_workspace.intent_continuation_runtime import continue_intent
from odin_backend.core.autonomous_workspace.session_prediction_engine import predict
from odin_backend.core.autonomous_workspace.workflow_recovery_system import recover
from odin_backend.core.autonomous_workspace.workspace_continuity_v2 import load_graph, save_graph


class AutonomousWorkspaceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._path = "./data/autonomous_workspace.json"
        self._history: list[str] = []

    async def open(self, *, project: str = "local") -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_workspace_enabled", False):
            return {"accepted": False, "reason": "autonomous_workspace_disabled"}
        graph = {"project": project, "nodes": []}
        if hasattr(self._app, "cognitive_kernel"):
            await self._app.cognitive_kernel.restore()
        save_graph(path=self._path, graph=graph)
        return {"accepted": True, "graph": graph, "supervised": True}

    async def predict_next(self) -> dict[str, Any]:
        pred = predict(history=self._history)
        self._emit("workspace_prediction_generated", pred)
        return {"accepted": True, **pred}

    async def recover_workflow(self) -> dict[str, Any]:
        rec = await recover(self._app)
        cont = continue_intent(intent=rec.get("narrative", "engineering"))
        self._emit("workflow_resumed", cont)
        return {"accepted": True, "recovery": rec, "continuation": cont}

    async def daily_resume(self) -> dict[str, Any]:
        p = await plan(self._app)
        restored = load_graph(path=self._path)
        return {"accepted": True, "plan": p, "workspace": restored}

    def snapshot(self) -> dict[str, Any]:
        return {"history_len": len(self._history)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_workspace")
''')

w("autonomous_workspace/__init__.py", '''from odin_backend.core.autonomous_workspace.autonomous_workspace_runtime import AutonomousWorkspaceRuntime
__all__ = ["AutonomousWorkspaceRuntime"]
''')

# --- autonomous_engineering_evolution ---
w("autonomous_engineering_evolution/repo_evolution_analyzer.py", '''from __future__ import annotations


def analyze(*, repo: str) -> dict:
    return {"repo": repo, "drift_score": 0.35, "modules": 12}
''')

w("autonomous_engineering_evolution/refactor_opportunity_detector.py", '''from __future__ import annotations


def detect(*, files: list[str]) -> list[str]:
    return [f for f in files if len(f) > 20][:3]
''')

w("autonomous_engineering_evolution/technical_debt_predictor.py", '''from __future__ import annotations


def predict_debt(*, churn: int) -> dict:
    risk = min(1.0, churn / 100.0)
    return {"risk": risk, "debt_likely": risk > 0.5}
''')

w("autonomous_engineering_evolution/patch_simulation_engine.py", '''from __future__ import annotations


def simulate(*, patch: str) -> dict:
    return {"simulated": True, "patch_len": len(patch), "auto_merge": False}
''')

w("autonomous_engineering_evolution/upgrade_planning_runtime.py", '''from __future__ import annotations
from typing import Any


class UpgradePlanningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def plan(self, *, goal: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_evolution_enabled", False):
            return {"accepted": False, "reason": "engineering_evolution_disabled"}
        proposal = {"goal": goal[:80], "approval_required": True, "rollback_plan": "mandatory"}
        self._emit("engineering_upgrade_proposed", proposal)
        return {"accepted": True, "proposal": proposal, "auto_deploy": False}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="upgrade_planning")
''')

w("autonomous_engineering_evolution/engineering_evolution_runtime.py", '''"""Autonomous engineering evolution (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.autonomous_engineering_evolution.patch_simulation_engine import simulate
from odin_backend.core.autonomous_engineering_evolution.refactor_opportunity_detector import detect
from odin_backend.core.autonomous_engineering_evolution.repo_evolution_analyzer import analyze
from odin_backend.core.autonomous_engineering_evolution.technical_debt_predictor import predict_debt
from odin_backend.core.autonomous_engineering_evolution.upgrade_planning_runtime import UpgradePlanningRuntime


class EngineeringEvolutionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._planner = UpgradePlanningRuntime(app)

    async def analyze_repo(self, *, repo: str = "local") -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_evolution_enabled", False):
            return {"accepted": False, "reason": "engineering_evolution_disabled"}
        evo = analyze(repo=repo)
        debt = predict_debt(churn=24)
        if debt.get("debt_likely"):
            self._emit("technical_debt_detected", debt)
        refs = detect(files=[f"{repo}/core", f"{repo}/api"])
        return {"accepted": True, "evolution": evo, "debt": debt, "refactors": refs, "supervised": True}

    async def simulate_patch(self, *, patch: str) -> dict[str, Any]:
        sim = simulate(patch=patch)
        if hasattr(self._app, "self_improvement_sandbox"):
            await self._app.self_improvement_sandbox.experiment(name="patch-sim")
        return {"accepted": True, **sim}

    async def propose_upgrade(self, *, goal: str) -> dict[str, Any]:
        return await self._planner.plan(goal=goal)

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="engineering_evolution")
''')

w("autonomous_engineering_evolution/__init__.py", '''from odin_backend.core.autonomous_engineering_evolution.engineering_evolution_runtime import EngineeringEvolutionRuntime
from odin_backend.core.autonomous_engineering_evolution.upgrade_planning_runtime import UpgradePlanningRuntime
__all__ = ["EngineeringEvolutionRuntime", "UpgradePlanningRuntime"]
''')

# --- cognitive_daemon v2 extensions ---
w("cognitive_daemon/deferred_reasoning_store.py", '''from __future__ import annotations
import json
from pathlib import Path


def defer(*, path: str, thought: str) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    items = []
    if p.exists():
        items = json.loads(p.read_text(encoding="utf-8"))
    items.append(thought[:160])
    p.write_text(json.dumps(items[-32:]), encoding="utf-8")
    return {"deferred": True}


def restore(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False, "thoughts": []}
    return {"restored": True, "thoughts": json.loads(p.read_text(encoding="utf-8"))}
''')

w("cognitive_daemon/overnight_cycles.py", '''from __future__ import annotations
from typing import Any


async def run(app: Any) -> dict:
    if hasattr(app, "cognitive_orchestration"):
        return await app.cognitive_orchestration.overnight_cycle()
    return {"cycle": "lightweight"}
''')

w("cognitive_daemon/low_power_mode.py", '''from __future__ import annotations


def transition(*, enabled: bool) -> dict:
    return {"low_power": enabled, "fps_cap": 8 if enabled else 30}
''')

w("cognitive_daemon/memory_consolidation.py", '''from __future__ import annotations
from typing import Any


async def consolidate(app: Any) -> dict:
    if hasattr(app, "memory_fabric"):
        return await app.memory_fabric.recall()
    return {"consolidated": False}
''')

w("cognitive_daemon/daemon_v2_runtime.py", '''"""Cognitive daemon V2 extensions (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_daemon.deferred_reasoning_store import defer, restore
from odin_backend.core.cognitive_daemon.low_power_mode import transition
from odin_backend.core.cognitive_daemon.memory_consolidation import consolidate
from odin_backend.core.cognitive_daemon.overnight_cycles import run


class CognitiveDaemonV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._path = "./data/deferred_reasoning.json"
        self._low_power = False

    async def overnight(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_daemon_v2_enabled", False):
            return {"accepted": False, "reason": "cognitive_daemon_v2_disabled"}
        cycle = await run(self._app)
        mem = await consolidate(self._app)
        self._emit("overnight_cycle_completed", {"completed": True})
        self._emit("overnight_optimization_completed", {"completed": True})
        return {"accepted": True, "cycle": cycle, "memory": mem}

    async def defer_thought(self, *, thought: str) -> dict[str, Any]:
        defer(path=self._path, thought=thought)
        return {"accepted": True, "deferred": True}

    async def restore_deferred(self) -> dict[str, Any]:
        r = restore(path=self._path)
        if r.get("restored"):
            self._emit("deferred_reasoning_restored", {"count": len(r.get("thoughts", []))})
        return {"accepted": True, **r}

    async def resume_cognition(self) -> dict[str, Any]:
        restored = await self.restore_deferred()
        if hasattr(self._app, "cognitive_daemon"):
            await self._app.cognitive_daemon.tick(idle_s=0)
        self._emit("cognitive_resume_completed", {"resumed": True})
        return {"accepted": True, "restored": restored}

    async def set_low_power(self, *, enabled: bool = True) -> dict[str, Any]:
        self._low_power = enabled
        t = transition(enabled=enabled)
        self._emit("low_power_transition", t)
        return {"accepted": True, **t}

    def snapshot(self) -> dict[str, Any]:
        return {"low_power": self._low_power}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_daemon_v2")
''')

# update cognitive_daemon __init__ in bootstrap - we'll patch separately

# --- operator_intelligence_v2 ---
w("operator_intelligence_v2/operator_behavior_model.py", '''from __future__ import annotations


class OperatorBehaviorModel:
    def __init__(self) -> None:
        self._sessions = 0

    def observe(self) -> dict:
        self._sessions += 1
        return {"sessions": self._sessions}
''')

w("operator_intelligence_v2/workflow_pattern_analyzer.py", '''from __future__ import annotations


def analyze(*, switches: int) -> dict:
    return {"switches": switches, "pattern": "deep_work" if switches < 5 else "fragmented"}
''')

w("operator_intelligence_v2/cognitive_fatigue_detector.py", '''from __future__ import annotations


def detect(*, hours: float) -> dict:
    fatigued = hours > 8
    return {"fatigued": fatigued, "hours": hours}
''')

w("operator_intelligence_v2/productivity_strategy_runtime.py", '''from __future__ import annotations
from typing import Any


async def strategy(app: Any) -> dict:
    if hasattr(app, "operator_productivity"):
        return await app.operator_productivity.summary()
    return {"strategy": "25m focus blocks"}
''')

w("operator_intelligence_v2/adaptive_assistance_runtime.py", '''from __future__ import annotations
from typing import Any


class AdaptiveAssistanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._intensity = 0.5

    async def adjust(self, *, fatigue: bool = False) -> dict[str, Any]:
        self._intensity = 0.3 if fatigue else 0.6
        self._emit("adaptive_assistance_adjusted", {"intensity": self._intensity})
        self._emit("attention_heatmap_updated", {"cells": [20, 40, 60]})
        return {"accepted": True, "intensity": self._intensity, "transparent": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_intelligence_v2")
''')

w("operator_intelligence_v2/intelligence_runtime.py", '''"""Operator intelligence V2 (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.operator_intelligence_v2.adaptive_assistance_runtime import AdaptiveAssistanceRuntime
from odin_backend.core.operator_intelligence_v2.cognitive_fatigue_detector import detect
from odin_backend.core.operator_intelligence_v2.operator_behavior_model import OperatorBehaviorModel
from odin_backend.core.operator_intelligence_v2.productivity_strategy_runtime import strategy
from odin_backend.core.operator_intelligence_v2.workflow_pattern_analyzer import analyze


class OperatorIntelligenceV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._behavior = OperatorBehaviorModel()
        self._assistance = AdaptiveAssistanceRuntime(app)

    async def analyze(self, *, hours: float = 4.0, switches: int = 3) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_intelligence_v2_enabled", False):
            return {"accepted": False, "reason": "operator_intelligence_v2_disabled"}
        obs = self._behavior.observe()
        patterns = analyze(switches=switches)
        fatigue = detect(hours=hours)
        if fatigue.get("fatigued"):
            self._emit("cognitive_fatigue_detected", fatigue)
        strat = await strategy(self._app)
        assist = await self._assistance.adjust(fatigue=fatigue.get("fatigued", False))
        return {
            "accepted": True,
            "behavior": obs,
            "patterns": patterns,
            "fatigue": fatigue,
            "strategy": strat,
            "assistance": assist,
            "local_only": True,
            "operator_controlled": True,
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_intelligence_v2")
''')

w("operator_intelligence_v2/__init__.py", '''from odin_backend.core.operator_intelligence_v2.intelligence_runtime import OperatorIntelligenceV2Runtime
__all__ = ["OperatorIntelligenceV2Runtime"]
''')

print("bootstrap_p49_core complete")

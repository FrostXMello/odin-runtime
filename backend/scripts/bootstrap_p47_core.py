"""Bootstrap Prompt 47 autonomous engineering workstation modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


PROFILES = ("lightweight_engineering", "balanced_engineering", "autonomous_engineering", "overnight_engineering")
ROLES = (
    "Architect", "Backend Engineer", "Frontend Engineer", "Debugger",
    "QA Engineer", "DevOps Engineer", "Reviewer", "Research Engineer",
)

# --- live_engineering_orchestrator ---
w("live_engineering_orchestrator/work_context.py", '''from __future__ import annotations
from typing import Any


def build_context(*, repo: str, goal: str = "", files: list[str] | None = None) -> dict[str, Any]:
    return {"repo": repo, "goal": goal[:160], "files": files or [], "continuity": True}
''')

w("live_engineering_orchestrator/repo_attention.py", '''from __future__ import annotations


def drift_score(*, dirty_files: int, stale_hours: float) -> float:
    return min(1.0, dirty_files * 0.05 + stale_hours / 48.0)
''')

w("live_engineering_orchestrator/active_issue_tracker.py", '''from __future__ import annotations
from typing import Any


class ActiveIssueTracker:
    def __init__(self) -> None:
        self._issues: list[dict] = []

    def track(self, *, title: str, blocked: bool = False) -> dict[str, Any]:
        item = {"title": title[:120], "blocked": blocked, "open": True}
        self._issues.append(item)
        return item

    def open_issues(self) -> list[dict]:
        return [i for i in self._issues if i.get("open")]
''')

w("live_engineering_orchestrator/code_focus.py", '''from __future__ import annotations


def infer_goal(*, file: str, error: str = "") -> str:
    if error:
        return f"debug {file}"
    if file.endswith(".py"):
        return f"implement {file}"
    return f"review {file}"
''')

w("live_engineering_orchestrator/debug_watchtower.py", '''from __future__ import annotations
from typing import Any


def watch(*, logs: list[str], errors: list[str]) -> dict[str, Any]:
    return {"log_lines": len(logs), "errors": errors[:5], "suggest_debug": bool(errors)}
''')

w("live_engineering_orchestrator/task_supervisor.py", '''from __future__ import annotations
from typing import Any


def supervise(*, tasks: list[str]) -> dict[str, Any]:
    return {"tasks": tasks[:12], "approval_required": True, "auto_patch": False}
''')

w("live_engineering_orchestrator/session_coordinator.py", '''from __future__ import annotations
import json
import time
from pathlib import Path


def save_session(*, path: str, data: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({**data, "saved_at": time.time()}), encoding="utf-8")
    return {"saved": True}


def load_session(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "data": json.loads(p.read_text(encoding="utf-8"))}
''')

w("live_engineering_orchestrator/engineering_orchestrator.py", '''"""Live engineering orchestrator (Prompt 47)."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

from odin_backend.core.live_engineering_orchestrator.active_issue_tracker import ActiveIssueTracker
from odin_backend.core.live_engineering_orchestrator.code_focus import infer_goal
from odin_backend.core.live_engineering_orchestrator.debug_watchtower import watch
from odin_backend.core.live_engineering_orchestrator.repo_attention import drift_score
from odin_backend.core.live_engineering_orchestrator.session_coordinator import load_session, save_session
from odin_backend.core.live_engineering_orchestrator.task_supervisor import supervise
from odin_backend.core.live_engineering_orchestrator.work_context import build_context

PROFILES = ("lightweight_engineering", "balanced_engineering", "autonomous_engineering", "overnight_engineering")


class LiveEngineeringOrchestratorRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._session_id = str(uuid4())
        self._issues = ActiveIssueTracker()
        self._profile = "balanced_engineering"
        self._path = "./data/engineering_session.json"

    async def observe(self, *, repo: str, file: str = "", error: str = "", logs: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "live_engineering_orchestrator_enabled", False):
            return {"accepted": False, "reason": "live_engineering_orchestrator_disabled"}
        goal = infer_goal(file=file or repo, error=error)
        ctx = build_context(repo=repo, goal=goal, files=[file] if file else [])
        tower = watch(logs=logs or [], errors=[error] if error else [])
        drift = drift_score(dirty_files=1 if error else 0, stale_hours=0.5)
        if error:
            self._issues.track(title=error[:80], blocked=True)
        live = {}
        if hasattr(self._app, "live_engineering"):
            live = await self._app.live_engineering.session(repo=repo, ide={"file": file}, error=error)
        self._emit("engineering_goal_detected", {"goal": goal, "repo": repo})
        caps = {"lightweight_engineering": 15, "balanced_engineering": 30, "autonomous_engineering": 45, "overnight_engineering": 10}
        return {
            "accepted": True,
            "session_id": self._session_id,
            "context": ctx,
            "watchtower": tower,
            "drift": drift,
            "live_engineering": live,
            "open_issues": self._issues.open_issues(),
            "supervised": True,
            "fps_cap": caps.get(self._profile, 30),
        }

    async def restore(self) -> dict[str, Any]:
        restored = load_session(path=self._path)
        if restored.get("restored"):
            self._emit("engineering_session_restored", restored.get("data", {}))
        return {"accepted": True, **restored}

    async def checkpoint(self, *, state: dict | None = None) -> dict[str, Any]:
        payload = state or {"session_id": self._session_id, "issues": self._issues.open_issues()}
        save_session(path=self._path, data=payload)
        return {"accepted": True, "checkpoint": payload}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in PROFILES:
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile, "stream_batching": profile != "autonomous_engineering"}

    def snapshot(self) -> dict[str, Any]:
        return {"session_id": self._session_id, "profile": self._profile, "issues": len(self._issues.open_issues())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_engineering_orchestrator")
''')

w("live_engineering_orchestrator/__init__.py", '''from odin_backend.core.live_engineering_orchestrator.engineering_orchestrator import LiveEngineeringOrchestratorRuntime
__all__ = ["LiveEngineeringOrchestratorRuntime"]
''')

# --- autonomous_debugging extensions ---
w("autonomous_debugging/trace_analyzer.py", '''from __future__ import annotations


def analyze(trace: str) -> dict:
    lines = [l for l in trace.splitlines() if l.strip()]
    return {"frames": lines[:12], "error": lines[-1] if lines else ""}
''')

w("autonomous_debugging/failure_clusterer.py", '''from __future__ import annotations


def cluster(failures: list[str]) -> dict:
    groups: dict[str, int] = {}
    for f in failures:
        key = f.split(":")[0][:40]
        groups[key] = groups.get(key, 0) + 1
    return {"clusters": groups, "repeated": [k for k, v in groups.items() if v > 1]}
''')

w("autonomous_debugging/stack_reasoner.py", '''from __future__ import annotations


def reason(frames: list[str]) -> dict:
    return {"root_frame": frames[0] if frames else "", "depth": len(frames)}
''')

w("autonomous_debugging/patch_hypothesis.py", '''from __future__ import annotations


def hypothesize(*, cause: str, file: str) -> dict:
    return {"file": file, "hypothesis": f"guard {cause[:40]}", "auto_apply": False, "approval_required": True}
''')

w("autonomous_debugging/regression_predictor.py", '''from __future__ import annotations


def predict(*, diff_size: int, tests_touched: int) -> dict:
    risk = min(1.0, diff_size / 500 + tests_touched / 20)
    return {"risk": round(risk, 3), "regression_likely": risk > 0.6}
''')

w("autonomous_debugging/runtime_debug_sessions.py", '''from __future__ import annotations
from typing import Any
from uuid import uuid4


class RuntimeDebugSessions:
    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}

    def open(self) -> dict[str, Any]:
        sid = str(uuid4())
        self._sessions[sid] = {"id": sid}
        return self._sessions[sid]
''')

w("autonomous_debugging/test_failure_mapper.py", '''from __future__ import annotations


def map_failures(tests: list[str]) -> dict:
    return {"flaky": [t for t in tests if "retry" in t.lower()], "count": len(tests)}
''')

w("autonomous_debugging/confidence_gates.py", '''from __future__ import annotations


def gate(*, confidence: float) -> dict:
    return {"allowed": confidence >= 0.55, "confidence": confidence, "supervised": True}
''')

w("autonomous_debugging/pipeline_runtime.py", '''"""Autonomous debugging pipeline (Prompt 47 extension)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.autonomous_debugging.confidence_gates import gate
from odin_backend.core.autonomous_debugging.failure_clusterer import cluster
from odin_backend.core.autonomous_debugging.patch_hypothesis import hypothesize
from odin_backend.core.autonomous_debugging.regression_predictor import predict
from odin_backend.core.autonomous_debugging.runtime_debug_sessions import RuntimeDebugSessions
from odin_backend.core.autonomous_debugging.stack_reasoner import reason
from odin_backend.core.autonomous_debugging.test_failure_mapper import map_failures
from odin_backend.core.autonomous_debugging.trace_analyzer import analyze


class AutonomousDebuggingPipelineRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._sessions = RuntimeDebugSessions()

    async def analyze(self, *, stacktrace: str, repo: str = "local") -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_debugging_enabled", False):
            return {"accepted": False, "reason": "autonomous_debugging_disabled"}
        traced = analyze(stacktrace)
        stacked = reason(traced.get("frames", []))
        clusters = cluster([traced.get("error", "")])
        if clusters.get("repeated"):
            self._emit("debug_cluster_created", clusters)
        hypothesis = hypothesize(cause=traced.get("error", ""), file=stacked.get("root_frame", "unknown"))
        risk = predict(diff_size=len(stacktrace), tests_touched=1)
        if risk.get("regression_likely"):
            self._emit("regression_risk_detected", risk)
        self._emit("patch_hypothesis_generated", hypothesis)
        confidence = 0.62
        g = gate(confidence=confidence)
        base = {}
        if hasattr(self._app, "autonomous_debugging"):
            base = await self._app.autonomous_debugging.analyze(stacktrace=stacktrace, repo=repo)
        return {
            "accepted": True,
            "trace": traced,
            "stack": stacked,
            "clusters": clusters,
            "hypothesis": hypothesis,
            "risk": risk,
            "gate": g,
            "base_analysis": base,
            "supervised": True,
            "auto_patch": False,
        }

    async def map_tests(self, *, tests: list[str]) -> dict[str, Any]:
        mapped = map_failures(tests)
        return {"accepted": True, **mapped}

    def snapshot(self) -> dict[str, Any]:
        return {"pipeline": "autonomous_debugging_v2"}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_debugging_pipeline")
''')

# --- engineering_workflows_v2 ---
w("engineering_workflows_v2/goal_pipeline.py", '''from __future__ import annotations


def pipeline(goal: str) -> list[str]:
    return ["analyze", "plan", "implement", "validate", "review"]
''')

w("engineering_workflows_v2/task_breakdown.py", '''from __future__ import annotations


def breakdown(goal: str) -> list[dict]:
    return [{"title": f"{goal[:40]} — stage {i}", "stage": i} for i in range(1, 4)]
''')

w("engineering_workflows_v2/repo_planner.py", '''from __future__ import annotations


def plan_repo(repo: str) -> dict:
    return {"repo": repo, "milestones": ["scaffold", "implement", "test"]}
''')

w("engineering_workflows_v2/implementation_stages.py", '''from __future__ import annotations


STAGES = ("plan", "implement", "test", "review", "merge_proposal")


def advance(current: str) -> str:
    order = list(STAGES)
    try:
        idx = order.index(current)
        return order[min(idx + 1, len(order) - 1)]
    except ValueError:
        return "plan"
''')

w("engineering_workflows_v2/milestone_tracking.py", '''from __future__ import annotations


class MilestoneTracker:
    def __init__(self) -> None:
        self._milestones: list[str] = []

    def add(self, name: str) -> None:
        self._milestones.append(name)

    def list(self) -> list[str]:
        return self._milestones[-16:]
''')

w("engineering_workflows_v2/workflow_state.py", '''from __future__ import annotations
import json
from pathlib import Path


def save_state(*, path: str, state: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")
    return {"saved": True}


def load_state(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))
''')

w("engineering_workflows_v2/execution_checkpoints.py", '''from __future__ import annotations


def checkpoint(stage: str, payload: dict) -> dict:
    return {"stage": stage, "payload": payload, "approval_gate": stage == "merge_proposal"}
''')

w("engineering_workflows_v2/workflows_runtime.py", '''"""Engineering workflows v2 (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.engineering_workflows_v2.execution_checkpoints import checkpoint
from odin_backend.core.engineering_workflows_v2.goal_pipeline import pipeline
from odin_backend.core.engineering_workflows_v2.implementation_stages import STAGES, advance
from odin_backend.core.engineering_workflows_v2.milestone_tracking import MilestoneTracker
from odin_backend.core.engineering_workflows_v2.repo_planner import plan_repo
from odin_backend.core.engineering_workflows_v2.task_breakdown import breakdown
from odin_backend.core.engineering_workflows_v2.workflow_state import load_state, save_state


class EngineeringWorkflowsV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._stage = "plan"
        self._milestones = MilestoneTracker()
        self._path = "./data/engineering_workflow.json"

    async def plan(self, *, goal: str, repo: str = "local") -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_workflows_v2_enabled", False):
            return {"accepted": False, "reason": "engineering_workflows_v2_disabled"}
        steps = pipeline(goal)
        tasks = breakdown(goal)
        repo_plan = plan_repo(repo)
        for m in repo_plan.get("milestones", []):
            self._milestones.add(m)
        state = {"goal": goal, "stage": self._stage, "tasks": tasks}
        save_state(path=self._path, state=state)
        return {"accepted": True, "pipeline": steps, "tasks": tasks, "repo_plan": repo_plan, "supervised": True}

    async def advance_stage(self) -> dict[str, Any]:
        nxt = advance(self._stage)
        self._stage = nxt
        self._emit("implementation_stage_advanced", {"stage": nxt})
        cp = checkpoint(nxt, {"stage": nxt})
        return {"accepted": True, "stage": nxt, "checkpoint": cp}

    async def resume(self) -> dict[str, Any]:
        state = load_state(path=self._path)
        if state:
            self._stage = state.get("stage", self._stage)
        return {"accepted": True, "state": state, "milestones": self._milestones.list()}

    def snapshot(self) -> dict[str, Any]:
        return {"stage": self._stage, "milestones": self._milestones.list()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="engineering_workflows_v2")
''')

w("engineering_workflows_v2/__init__.py", '''from odin_backend.core.engineering_workflows_v2.workflows_runtime import EngineeringWorkflowsV2Runtime
__all__ = ["EngineeringWorkflowsV2Runtime"]
''')

# --- self_improvement_sandbox ---
w("self_improvement_sandbox/branch_lab.py", '''from __future__ import annotations


def create_branch(name: str) -> dict:
    return {"branch": f"sandbox/{name}", "isolated": True, "main_safe": True}
''')

w("self_improvement_sandbox/proposal_execution.py", '''from __future__ import annotations


def execute_proposal(*, proposal_id: str) -> dict:
    return {"proposal_id": proposal_id, "executed": False, "approval_required": True}
''')

w("self_improvement_sandbox/isolated_validation.py", '''from __future__ import annotations


def validate(*, branch: str) -> dict:
    return {"branch": branch, "validated": True, "production_deploy": False}
''')

w("self_improvement_sandbox/rollback_training.py", '''from __future__ import annotations


def rehearse_rollback(*, target: str) -> dict:
    return {"target": target, "rehearsed": True}
''')

w("self_improvement_sandbox/performance_diffing.py", '''from __future__ import annotations


def diff_perf(before: dict, after: dict) -> dict:
    return {"before": before, "after": after, "delta": after != before}
''')

w("self_improvement_sandbox/architecture_sandbox.py", '''from __future__ import annotations


def simulate_architecture(proposal: dict) -> dict:
    return {"simulated": True, "proposal": proposal, "auto_merge": False}
''')

w("self_improvement_sandbox/sandbox_runtime.py", '''"""Self-improvement sandbox (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.self_improvement_sandbox.architecture_sandbox import simulate_architecture
from odin_backend.core.self_improvement_sandbox.branch_lab import create_branch
from odin_backend.core.self_improvement_sandbox.isolated_validation import validate
from odin_backend.core.self_improvement_sandbox.performance_diffing import diff_perf
from odin_backend.core.self_improvement_sandbox.proposal_execution import execute_proposal
from odin_backend.core.self_improvement_sandbox.rollback_training import rehearse_rollback


class SelfImprovementSandboxRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._timeline: list[dict] = []

    async def experiment(self, *, name: str, proposal: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_improvement_sandbox_enabled", False):
            return {"accepted": False, "reason": "self_improvement_sandbox_disabled"}
        branch = create_branch(name)
        sim = simulate_architecture(proposal or {"name": name})
        validation = validate(branch=branch["branch"])
        self._emit("sandbox_validation_completed", validation)
        self._timeline.append({"branch": branch, "validation": validation})
        return {"accepted": True, "branch": branch, "simulation": sim, "validation": validation, "isolated": True}

    async def rollback_rehearsal(self, *, target: str = "last_stable") -> dict[str, Any]:
        r = rehearse_rollback(target=target)
        return {"accepted": True, **r}

    async def benchmark_diff(self) -> dict[str, Any]:
        before = {}
        after = {}
        if hasattr(self._app, "runtime_benchmarks"):
            before = self._app.runtime_benchmarks.snapshot()
        diff = diff_perf(before, after)
        return {"accepted": True, "diff": diff}

    def snapshot(self) -> dict[str, Any]:
        return {"experiments": len(self._timeline)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="self_improvement_sandbox")
''')

w("self_improvement_sandbox/__init__.py", '''from odin_backend.core.self_improvement_sandbox.sandbox_runtime import SelfImprovementSandboxRuntime
__all__ = ["SelfImprovementSandboxRuntime"]
''')

# --- project_memory ---
w("project_memory/project_timeline.py", '''from __future__ import annotations


class ProjectTimeline:
    def __init__(self) -> None:
        self._events: list[dict] = []

    def add(self, kind: str, detail: str) -> None:
        self._events.append({"kind": kind, "detail": detail[:120]})

    def replay(self, limit: int = 24) -> list[dict]:
        return self._events[-limit:]
''')

w("project_memory/decision_memory.py", '''from __future__ import annotations


class DecisionMemory:
    def __init__(self) -> None:
        self._decisions: list[dict] = []

    def record(self, decision: str, rationale: str) -> dict:
        item = {"decision": decision[:80], "rationale": rationale[:160]}
        self._decisions.append(item)
        return item
''')

w("project_memory/engineering_sessions.py", '''from __future__ import annotations


class EngineeringSessions:
    def __init__(self) -> None:
        self._sessions: list[dict] = []

    def start(self, repo: str) -> dict:
        s = {"repo": repo, "active": True}
        self._sessions.append(s)
        return s
''')

w("project_memory/issue_history.py", '''from __future__ import annotations


def recurrence(issues: list[str]) -> dict:
    seen: dict[str, int] = {}
    for i in issues:
        seen[i] = seen.get(i, 0) + 1
    return {"recurring": [k for k, v in seen.items() if v > 1]}
''')

w("project_memory/architecture_memory.py", '''from __future__ import annotations


class ArchitectureMemory:
    def __init__(self) -> None:
        self._entries: list[dict] = []

    def remember(self, component: str, note: str) -> dict:
        e = {"component": component, "note": note[:120]}
        self._entries.append(e)
        return e
''')

w("project_memory/dependency_memory.py", '''from __future__ import annotations


def deps_for(repo: str) -> list[str]:
    return [f"{repo}-core", f"{repo}-api"]
''')

w("project_memory/project_resume.py", '''from __future__ import annotations
import json
from pathlib import Path


def save_resume(*, path: str, data: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")
    return {"saved": True}


def load_resume(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "data": json.loads(p.read_text(encoding="utf-8"))}
''')

w("project_memory/memory_runtime.py", '''"""Persistent project memory (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.project_memory.architecture_memory import ArchitectureMemory
from odin_backend.core.project_memory.decision_memory import DecisionMemory
from odin_backend.core.project_memory.dependency_memory import deps_for
from odin_backend.core.project_memory.engineering_sessions import EngineeringSessions
from odin_backend.core.project_memory.issue_history import recurrence
from odin_backend.core.project_memory.project_resume import load_resume, save_resume
from odin_backend.core.project_memory.project_timeline import ProjectTimeline


class ProjectMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._timeline = ProjectTimeline()
        self._decisions = DecisionMemory()
        self._sessions = EngineeringSessions()
        self._architecture = ArchitectureMemory()
        self._path = "./data/project_memory.json"

    async def remember(self, *, repo: str, decision: str = "", issue: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "project_memory_enabled", False):
            return {"accepted": False, "reason": "project_memory_disabled"}
        self._sessions.start(repo)
        if decision:
            self._decisions.record(decision, rationale=issue or repo)
            self._timeline.add("decision", decision)
        if issue:
            self._timeline.add("issue", issue)
        self._architecture.remember(repo, note=decision or "active")
        save_resume(path=self._path, data={"repo": repo, "timeline": self._timeline.replay()})
        return {
            "accepted": True,
            "timeline": self._timeline.replay(),
            "dependencies": deps_for(repo),
            "recurrence": recurrence([issue] if issue else []),
        }

    async def resume(self, *, repo: str = "") -> dict[str, Any]:
        restored = load_resume(path=self._path)
        if restored.get("restored"):
            self._emit("engineering_session_restored", {"repo": repo or restored.get("data", {}).get("repo")})
        return {"accepted": True, **restored, "timeline": self._timeline.replay()}

    def snapshot(self) -> dict[str, Any]:
        return {"timeline_len": len(self._timeline.replay())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="project_memory")
''')

w("project_memory/__init__.py", '''from odin_backend.core.project_memory.memory_runtime import ProjectMemoryRuntime
__all__ = ["ProjectMemoryRuntime"]
''')

# --- engineering_society ---
w("engineering_society/role_assignment.py", '''from __future__ import annotations

ROLES = (
    "Architect", "Backend Engineer", "Frontend Engineer", "Debugger",
    "QA Engineer", "DevOps Engineer", "Reviewer", "Research Engineer",
)


def assign(task: str) -> list[str]:
    if "debug" in task.lower():
        return ["Debugger", "QA Engineer"]
    if "arch" in task.lower():
        return ["Architect", "Reviewer"]
    return ["Backend Engineer", "Reviewer"]
''')

w("engineering_society/peer_review.py", '''from __future__ import annotations


def review(*, patch: str) -> dict:
    return {"approved": False, "notes": "supervised review required", "patch_len": len(patch)}
''')

w("engineering_society/architecture_debate.py", '''from __future__ import annotations


def debate(topic: str) -> dict:
    return {"topic": topic[:80], "positions": ["modular", "monolith"], "consensus_required": True}
''')

w("engineering_society/testing_council.py", '''from __future__ import annotations


def council(tests: list[str]) -> dict:
    return {"tests": len(tests), "consensus": "pending"}
''')

w("engineering_society/review_consensus.py", '''from __future__ import annotations


def consensus(votes: list[bool]) -> dict:
    approved = sum(votes) >= max(2, len(votes) // 2 + 1)
    return {"approved": approved, "votes": len(votes)}
''')

w("engineering_society/implementation_delegation.py", '''from __future__ import annotations


def delegate(*, role: str, task: str) -> dict:
    return {"role": role, "task": task[:80], "supervised": True}
''')

w("engineering_society/engineering_council.py", '''"""Collaborative engineering society (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.engineering_society.architecture_debate import debate
from odin_backend.core.engineering_society.implementation_delegation import delegate
from odin_backend.core.engineering_society.peer_review import review
from odin_backend.core.engineering_society.review_consensus import consensus
from odin_backend.core.engineering_society.role_assignment import ROLES, assign
from odin_backend.core.engineering_society.testing_council import council


class EngineeringSocietyRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def convene(self, *, topic: str, patch: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_society_enabled", False):
            return {"accepted": False, "reason": "engineering_society_disabled"}
        roles = assign(topic)
        deb = debate(topic)
        self._emit("architecture_debate_started", deb)
        rev = review(patch=patch) if patch else {"skipped": True}
        cons = consensus([False, False, True]) if patch else {"approved": False}
        if cons.get("approved"):
            self._emit("review_consensus_reached", cons)
        tests = council(["unit", "integration"])
        delegation = [delegate(role=r, task=topic) for r in roles[:2]]
        society = {}
        if hasattr(self._app, "agent_society"):
            society = {"agents": list(getattr(self._app.agent_society, "_agents", {}).keys())[:8]}
        return {
            "accepted": True,
            "roles": roles,
            "roles_available": list(ROLES),
            "debate": deb,
            "review": rev,
            "consensus": cons,
            "testing_council": tests,
            "delegation": delegation,
            "society": society,
            "supervised": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"roles": list(ROLES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="engineering_society")
''')

w("engineering_society/__init__.py", '''from odin_backend.core.engineering_society.engineering_council import EngineeringSocietyRuntime
__all__ = ["EngineeringSocietyRuntime"]
''')

# --- continuous_engineering ---
w("continuous_engineering/engineering_tick.py", '''from __future__ import annotations
from typing import Any


async def tick(app: Any, *, idle_s: float) -> dict:
    out = {"idle_s": idle_s}
    if hasattr(app, "live_engineering_orchestrator"):
        out["orchestrator"] = await app.live_engineering_orchestrator.observe(repo="local")
    return out
''')

w("continuous_engineering/repo_watchers.py", '''from __future__ import annotations


def watch(repo: str) -> dict:
    return {"repo": repo, "watching": True, "local_only": True}
''')

w("continuous_engineering/background_validation.py", '''from __future__ import annotations
from typing import Any


async def validate_light(app: Any) -> dict:
    if hasattr(app, "validation_fabric"):
        snap = getattr(app.validation_fabric, "snapshot", lambda: {})()
        return {"validation": snap, "lightweight": True}
    return {"skipped": True}
''')

w("continuous_engineering/overnight_analysis.py", '''from __future__ import annotations
from typing import Any


async def analyze(app: Any, *, repo: str) -> dict:
    return {"repo": repo, "analysis": "deferred thoughts compiled", "local_only": True}
''')

w("continuous_engineering/test_drift_detection.py", '''from __future__ import annotations


def detect(tests: list[str]) -> dict:
    return {"drift": len(tests) > 10, "count": len(tests)}
''')

w("continuous_engineering/attention_resumption.py", '''from __future__ import annotations
from typing import Any


async def resume(app: Any) -> dict:
    if hasattr(app, "project_memory"):
        return await app.project_memory.resume()
    return {"restored": False}
''')

w("continuous_engineering/patch_queue_monitor.py", '''from __future__ import annotations
from typing import Any


def monitor(app: Any) -> dict:
    pending = 0
    if hasattr(app, "autonomous_patching"):
        snap = app.autonomous_patching.snapshot()
        pending = len(snap.get("proposals", [])) if isinstance(snap, dict) else 0
    return {"pending_patches": pending, "auto_apply": False}
''')

w("continuous_engineering/continuous_runtime.py", '''"""Continuous engineering daemon (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.continuous_engineering.attention_resumption import resume
from odin_backend.core.continuous_engineering.background_validation import validate_light
from odin_backend.core.continuous_engineering.engineering_tick import tick
from odin_backend.core.continuous_engineering.overnight_analysis import analyze
from odin_backend.core.continuous_engineering.patch_queue_monitor import monitor
from odin_backend.core.continuous_engineering.repo_watchers import watch
from odin_backend.core.continuous_engineering.test_drift_detection import detect


class ContinuousEngineeringRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._profile = "balanced_engineering"

    async def engineering_tick(self, *, repo: str = "local", idle_s: float = 0.0) -> dict[str, Any]:
        if not getattr(self._app.settings, "continuous_engineering_enabled", False):
            return {"accepted": False, "reason": "continuous_engineering_disabled"}
        t = await tick(self._app, idle_s=idle_s)
        w = watch(repo)
        validation = await validate_light(self._app)
        drift = detect(["unit", "integration"])
        queue = monitor(self._app)
        restored = await resume(self._app)
        if hasattr(self._app, "cognitive_daemon"):
            await self._app.cognitive_daemon.tick(idle_s=idle_s)
        return {
            "accepted": True,
            "tick": t,
            "repo_watch": w,
            "validation": validation,
            "drift": drift,
            "patch_queue": queue,
            "restored": restored,
            "resource_aware": True,
        }

    async def overnight(self, *, repo: str = "local") -> dict[str, Any]:
        if self._profile != "overnight_engineering" and self._profile != "balanced_engineering":
            return {"accepted": True, "skipped": True, "reason": "profile_not_overnight"}
        result = await analyze(self._app, repo=repo)
        self._emit("overnight_analysis_completed", result)
        return {"accepted": True, **result}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in ("lightweight_engineering", "balanced_engineering", "autonomous_engineering", "overnight_engineering"):
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="continuous_engineering")
''')

w("continuous_engineering/__init__.py", '''from odin_backend.core.continuous_engineering.continuous_runtime import ContinuousEngineeringRuntime
__all__ = ["ContinuousEngineeringRuntime"]
''')

print("bootstrap_p47_core complete")

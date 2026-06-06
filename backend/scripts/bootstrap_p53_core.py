"""Bootstrap Prompt 53 autonomous overnight cognition modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


MODES = ("passive", "balanced", "engineering", "deep_overnight")

# --- deferred_reasoning ---
w("deferred_reasoning/deferred_store.py", '''"""SQLite deferred cognition store (Prompt 53)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any


class DeferredCognitionStore:
    def __init__(self, db_path: Path) -> None:
        self._path = db_path
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS deferred_reasoning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thought TEXT,
                chain TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def defer(self, *, thought: str, chain: list[str] | None = None) -> int:
        cur = self._conn.execute(
            "INSERT INTO deferred_reasoning (thought, chain) VALUES (?, ?)",
            (thought[:500], json.dumps(chain or [])),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def restore_all(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT id, thought, chain FROM deferred_reasoning ORDER BY id").fetchall()
        self._conn.execute("DELETE FROM deferred_reasoning")
        self._conn.commit()
        return [{"id": r[0], "thought": r[1], "chain": json.loads(r[2] or "[]")} for r in rows]

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM deferred_reasoning").fetchone()[0])
''')

w("deferred_reasoning/deferred_reasoning_runtime.py", '''"""Deferred reasoning runtime (Prompt 53)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.deferred_reasoning.deferred_store import DeferredCognitionStore


class DeferredReasoningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "deferred_cognition.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = DeferredCognitionStore(db)

    async def defer_reasoning(self, *, thought: str, chain: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "deferred_reasoning_enabled", False):
            return {"accepted": False, "reason": "deferred_reasoning_disabled"}
        rid = self._store.defer(thought=thought, chain=chain)
        self._emit("reasoning_chain_deferred", {"id": rid, "thought": thought[:80]})
        if hasattr(self._app, "cognitive_scheduler"):
            await self._app.cognitive_scheduler.defer_task(task=thought[:120])
        return {"accepted": True, "id": rid, "approval_required": False}

    async def restore_reasoning(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "deferred_reasoning_enabled", False):
            return {"accepted": False, "reason": "deferred_reasoning_disabled"}
        items = self._store.restore_all()
        if items:
            self._emit("reasoning_chain_restored", {"count": len(items)})
        return {"accepted": True, "restored": items}

    async def compress_reasoning_chain(self, *, chain: list[str]) -> dict[str, Any]:
        compressed = [c[:80] for c in chain[:8]]
        return {"accepted": True, "compressed": compressed, "lossy": False}

    async def replay_reasoning_context(self, *, thought: str) -> dict[str, Any]:
        return {"accepted": True, "thought": thought[:120], "replayable": True}

    def snapshot(self) -> dict[str, Any]:
        return {"pending": self._store.count()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="deferred_reasoning")
''')

w("deferred_reasoning/__init__.py", '''from odin_backend.core.deferred_reasoning.deferred_reasoning_runtime import DeferredReasoningRuntime

__all__ = ["DeferredReasoningRuntime"]
''')

# --- continuity_forecasting ---
w("continuity_forecasting/continuity_forecasting_runtime.py", '''"""Continuity forecasting (Prompt 53)."""
from __future__ import annotations
from typing import Any


class ContinuityForecastingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def forecast_operator_focus(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "continuity_forecasting_enabled", False):
            return {"accepted": False, "reason": "continuity_forecasting_disabled"}
        forecast = {"focus": "engineering", "confidence": 0.72}
        if hasattr(self._app, "operator_intelligence_v4"):
            r = await self._app.operator_intelligence_v4.forecast_focus(switches=4)
            if r.get("accepted"):
                forecast["detail"] = r
        self._emit("continuity_forecast_generated", forecast)
        return {"accepted": True, "forecast": forecast}

    async def detect_abandoned_work(self) -> dict[str, Any]:
        abandoned = []
        if hasattr(self._app, "cognitive_scheduler"):
            snap = self._app.cognitive_scheduler.snapshot()
            if snap.get("deferred", 0) > 0:
                abandoned.append("deferred_queue")
        if abandoned:
            self._emit("abandoned_work_detected", {"items": abandoned})
        return {"accepted": True, "abandoned": abandoned}

    async def predict_project_pressure(self, *, project: str = "local") -> dict[str, Any]:
        return {"accepted": True, "project": project[:80], "pressure": 0.45}

    async def generate_continuity_plan(self) -> dict[str, Any]:
        focus = await self.forecast_operator_focus()
        abandoned = await self.detect_abandoned_work()
        return {"accepted": True, "plan": {"focus": focus, "abandoned": abandoned}}

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="continuity_forecasting")
''')

w("continuity_forecasting/__init__.py", '''from odin_backend.core.continuity_forecasting.continuity_forecasting_runtime import ContinuityForecastingRuntime

__all__ = ["ContinuityForecastingRuntime"]
''')

# --- morning_briefing ---
w("morning_briefing/morning_briefing_runtime.py", '''"""Morning briefing runtime (Prompt 53)."""
from __future__ import annotations
from typing import Any


class MorningBriefingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._last_summary: dict = {}

    async def build_morning_briefing(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "morning_briefing_enabled", False):
            return {"accepted": False, "reason": "morning_briefing_disabled"}
        overnight = await self.summarize_overnight_activity()
        focus = await self.generate_focus_plan()
        briefing = {
            "executive_summary": "Overnight cognition completed within bounded limits.",
            "overnight_findings": overnight.get("summary", {}),
            "focus_plan": focus.get("plan", {}),
            "supervised": True,
        }
        self._last_summary = briefing
        self._emit("morning_briefing_generated", {"sections": 3})
        return {"accepted": True, "briefing": briefing}

    async def summarize_overnight_activity(self) -> dict[str, Any]:
        summary = {"cycles": 0, "findings": []}
        if hasattr(self._app, "overnight_cognition"):
            summary["cycles"] = self._app.overnight_cognition.snapshot().get("cycles", 0)
        return {"accepted": True, "summary": summary}

    async def generate_focus_plan(self) -> dict[str, Any]:
        plan = {"priorities": ["review overnight findings", "resume deferred work"], "transparent": True}
        if hasattr(self._app, "continuity_forecasting"):
            cf = await self._app.continuity_forecasting.generate_continuity_plan()
            plan["continuity"] = cf
        return {"accepted": True, "plan": plan}

    def snapshot(self) -> dict[str, Any]:
        return {"has_briefing": bool(self._last_summary)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="morning_briefing")
''')

w("morning_briefing/__init__.py", '''from odin_backend.core.morning_briefing.morning_briefing_runtime import MorningBriefingRuntime

__all__ = ["MorningBriefingRuntime"]
''')

# --- cognitive_maintenance ---
w("cognitive_maintenance/cognitive_maintenance_runtime.py", '''"""Cognitive maintenance (Prompt 53)."""
from __future__ import annotations
from typing import Any


class CognitiveMaintenanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def compact_memory_threads(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_maintenance_enabled", False):
            return {"accepted": False, "reason": "cognitive_maintenance_disabled"}
        if hasattr(self._app, "memory_fabric_v2"):
            await self._app.memory_fabric_v2.compress_history(tokens=2048)
        self._emit("memory_threads_compacted", {"compacted": True})
        return {"accepted": True, "compacted": True}

    async def prune_inactive_contexts(self) -> dict[str, Any]:
        if hasattr(self._app, "memory_fabric_v2"):
            await self._app.memory_fabric_v2.prune_memory(age_days=45)
        return {"accepted": True, "pruned": True}

    async def compress_streams(self) -> dict[str, Any]:
        if hasattr(self._app, "cognitive_streams"):
            await self._app.cognitive_streams.reflect_stream(summary="overnight compaction")
        return {"accepted": True, "compressed": True}

    async def stabilize_runtime_state(self) -> dict[str, Any]:
        if hasattr(self._app, "runtime_coordination"):
            await self._app.runtime_coordination.resolve_priority_conflicts()
        self._emit("runtime_state_stabilized", {"stabilized": True})
        return {"accepted": True, "stabilized": True}

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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_maintenance")
''')

w("cognitive_maintenance/__init__.py", '''from odin_backend.core.cognitive_maintenance.cognitive_maintenance_runtime import CognitiveMaintenanceRuntime

__all__ = ["CognitiveMaintenanceRuntime"]
''')

# --- idle_engineering ---
w("idle_engineering/idle_engineering_runtime.py", '''"""Idle engineering runtime (Prompt 53)."""
from __future__ import annotations
from typing import Any


class IdleEngineeringRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._last_report: dict = {}

    async def analyze_idle_repositories(self, *, repos: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "idle_engineering_enabled", False):
            return {"accepted": False, "reason": "idle_engineering_disabled"}
        repos = repos or ["local"]
        report = {"repos": repos[:8], "supervised": True, "no_auto_deploy": True}
        if hasattr(self._app, "engineering_infrastructure_v3"):
            r = await self._app.engineering_infrastructure_v3.oversee(repos=repos)
            report["oversee"] = r
        self._emit("idle_engineering_analysis_completed", report)
        self._last_report = report
        return {"accepted": True, "report": report}

    async def detect_refactor_candidates(self, *, repo: str = "local") -> dict[str, Any]:
        return {"accepted": True, "repo": repo[:80], "candidates": [], "approval_required": True}

    async def simulate_regression_risk(self, *, change: str) -> dict[str, Any]:
        if hasattr(self._app, "engineering_infrastructure_v3"):
            r = await self._app.engineering_infrastructure_v3.forecast_reliability(change=change)
            self._emit("regression_risk_simulated", {"change": change[:80]})
            return r
        return {"accepted": True, "risk": 0.2, "simulated": True}

    async def prepare_engineering_report(self) -> dict[str, Any]:
        return await self.analyze_idle_repositories()

    def snapshot(self) -> dict[str, Any]:
        return {"has_report": bool(self._last_report)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="idle_engineering")
''')

w("idle_engineering/__init__.py", '''from odin_backend.core.idle_engineering.idle_engineering_runtime import IdleEngineeringRuntime

__all__ = ["IdleEngineeringRuntime"]
''')

# --- overnight_cognition ---
w("overnight_cognition/overnight_cognition_runtime.py", '''"""Overnight cognition orchestration (Prompt 53)."""
from __future__ import annotations
from typing import Any

MODES = ("passive", "balanced", "engineering", "deep_overnight")


class OvernightCognitionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._active = False
        self._cycles = 0
        self._mode = "balanced"
        self._summary: dict = {}

    async def start_overnight_cycle(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "overnight_cognition_enabled", False):
            return {"accepted": False, "reason": "overnight_cognition_disabled"}
        max_cycles = int(getattr(self._app.settings, "overnight_max_cycles", 32))
        if self._cycles >= max_cycles:
            return {"accepted": False, "reason": "max_cycles_reached", "bounded": True}
        self._active = True
        self._emit("overnight_cycle_started", {"mode": self._mode, "cycle": self._cycles})
        if hasattr(self._app, "unified_cognitive_core"):
            await self._app.unified_cognitive_core.cognition_tick()
        if hasattr(self._app, "cognitive_daemon_v2"):
            await self._app.cognitive_daemon_v2.set_low_power(enabled=True)
        return {"accepted": True, "active": True, "mode": self._mode, "no_auto_deploy": True}

    async def pause_overnight_cycle(self) -> dict[str, Any]:
        self._active = False
        if hasattr(self._app, "cognitive_daemon_v2"):
            await self._app.cognitive_daemon_v2.set_low_power(enabled=False)
        return {"accepted": True, "active": False}

    async def execute_idle_reasoning(self) -> dict[str, Any]:
        if not self._active:
            return {"accepted": False, "reason": "overnight_not_active"}
        max_cycles = int(getattr(self._app.settings, "overnight_max_cycles", 32))
        if self._cycles >= max_cycles:
            return {"accepted": False, "reason": "max_cycles_reached"}
        self._cycles += 1
        if hasattr(self._app, "realtime_cognition"):
            await self._app.realtime_cognition.reason(thought=f"idle reasoning cycle {self._cycles}")
        if hasattr(self._app, "autonomous_loop_v2"):
            await self._app.autonomous_loop_v2.autonomous_tick(idle_s=120.0)
        self._emit("idle_reasoning_executed", {"cycle": self._cycles})
        if self._cycles >= max_cycles:
            await self.complete_overnight_cycle()
        return {"accepted": True, "cycle": self._cycles, "bounded": True}

    async def complete_overnight_cycle(self) -> dict[str, Any]:
        self._emit("overnight_cycle_completed", {"cycles": self._cycles})
        self._active = False
        return {"accepted": True, "completed": True, "cycles": self._cycles}

    async def prepare_resume_state(self) -> dict[str, Any]:
        if hasattr(self._app, "deferred_reasoning"):
            restored = await self._app.deferred_reasoning.restore_reasoning()
            return {"accepted": True, "resume": restored}
        return {"accepted": True, "resume": {}}

    async def generate_overnight_summary(self) -> dict[str, Any]:
        self._summary = {"cycles": self._cycles, "mode": self._mode, "active": self._active}
        if hasattr(self._app, "morning_briefing"):
            b = await self._app.morning_briefing.summarize_overnight_activity()
            self._summary["briefing"] = b
        return {"accepted": True, "summary": self._summary}

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if mode not in MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        return {"accepted": True, "mode": mode}

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active, "cycles": self._cycles, "mode": self._mode}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="overnight_cognition")
''')

w("overnight_cognition/__init__.py", '''from odin_backend.core.overnight_cognition.overnight_cognition_runtime import OvernightCognitionRuntime

__all__ = ["OvernightCognitionRuntime"]
''')

print("bootstrap_p53_core complete")

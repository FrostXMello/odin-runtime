"""Bootstrap Prompt 62 collaborative cognition modules."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "odin_backend" / "core"


def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


w("collaborative_cognition/collaborative_cognition_runtime.py", '''"""Collaborative cognition runtime (Prompt 62)."""
from __future__ import annotations
from typing import Any

PROFILES = ("solo", "pair", "team", "supervisory", "overnight_collaboration")


class CollaborativeCognitionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._initialized = False
        self._profile = "balanced"
        self._attention = 0.5
        self._sync_loops = 0
        self._surfaces: dict[str, str] = {}

    async def initialize_collaboration(self, *, profile: str = "team") -> dict[str, Any]:
        if not getattr(self._app.settings, "collaborative_cognition_enabled", False):
            return {"accepted": False, "reason": "collaborative_cognition_disabled"}
        if profile not in PROFILES:
            profile = getattr(self._app.settings, "collaboration_profile", "balanced")
        self._initialized = True
        self._profile = profile
        self._emit("collaborative_cognition_initialized", {"profile": self._profile})
        return {"accepted": True, "initialized": True, "profile": self._profile, "transparent": True}

    async def synchronize_operator_state(self) -> dict[str, Any]:
        if self._sync_loops > 48:
            return {"accepted": False, "reason": "collaboration_sync_bounded"}
        self._sync_loops += 1
        if hasattr(self._app, "operator_sessions"):
            await self._app.operator_sessions.synchronize_session_state()
        return {"accepted": True, "synchronized": True, "bounded": True}

    async def assign_cognition_surface(self, *, operator_id: str = "operator-local", surface: str = "shared-command") -> dict[str, Any]:
        self._surfaces[operator_id] = surface
        return {"accepted": True, "operator_id": operator_id, "surface": surface, "operator_visible": True}

    async def rebalance_shared_attention(self) -> dict[str, Any]:
        self._attention = max(0.1, self._attention - 0.05)
        if hasattr(self._app, "team_coordination"):
            await self._app.team_coordination.rebalance_team_attention()
        return {"accepted": True, "attention": round(self._attention, 2), "permission_aware": True}

    def snapshot(self) -> dict[str, Any]:
        return {"initialized": self._initialized, "profile": self._profile, "attention": self._attention, "surfaces": self._surfaces}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="collaborative_cognition")
''')
w("collaborative_cognition/__init__.py", '''from odin_backend.core.collaborative_cognition.collaborative_cognition_runtime import CollaborativeCognitionRuntime

__all__ = ["CollaborativeCognitionRuntime"]
''')

w("operator_sessions/session_store.py", '''"""SQLite collaborative operator session registry (Prompt 62)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

MAX_SESSIONS = 500


class OperatorSessionStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS operator_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator_id TEXT,
                role TEXT,
                payload TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            )"""
        )
        self._conn.commit()

    def create(self, *, operator_id: str, role: str, payload: dict[str, Any]) -> int:
        cur = self._conn.execute(
            "INSERT INTO operator_sessions (operator_id, role, payload) VALUES (?, ?, ?)",
            (operator_id[:80], role[:40], json.dumps(payload)),
        )
        count = self._conn.execute("SELECT COUNT(*) FROM operator_sessions").fetchone()[0]
        if count > MAX_SESSIONS:
            self._conn.execute(
                """DELETE FROM operator_sessions WHERE session_id NOT IN (
                    SELECT session_id FROM operator_sessions ORDER BY session_id DESC LIMIT ?
                )""",
                (MAX_SESSIONS,),
            )
        self._conn.commit()
        return cur.lastrowid or 0

    def sessions(self, *, limit: int = 50) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT session_id, operator_id, role, payload FROM operator_sessions ORDER BY session_id DESC LIMIT ?",
            (min(limit, MAX_SESSIONS),),
        ).fetchall()
        return [{"session_id": r[0], "operator_id": r[1], "role": r[2], **json.loads(r[3])} for r in rows]
''')
w("operator_sessions/operator_sessions_runtime.py", '''"""Operator sessions runtime (Prompt 62)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.operator_sessions.session_store import OperatorSessionStore


class OperatorSessionsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "operator_sessions.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = OperatorSessionStore(db)
        self._active: dict[str, dict[str, Any]] = {}

    async def create_operator_session(self, *, operator_id: str = "operator-local", role: str = "supervisor") -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_sessions_enabled", False):
            return {"accepted": False, "reason": "operator_sessions_disabled"}
        payload = {
            "active_missions": [],
            "approval_authority": role in {"supervisor", "admin"},
            "focus_state": "available",
            "runtime_ownership": [],
            "supervision_scope": "local",
        }
        sid = self._store.create(operator_id=operator_id, role=role, payload=payload)
        self._active[operator_id] = {"session_id": sid, "role": role, **payload}
        self._emit("operator_session_created", {"operator_id": operator_id[:40], "role": role})
        return {"accepted": True, "session_id": sid, "operator_id": operator_id, "role": role, "transparent": True}

    async def restore_operator_session(self, *, operator_id: str = "operator-local") -> dict[str, Any]:
        sessions = [s for s in self._store.sessions() if s["operator_id"] == operator_id]
        restored = sessions[0] if sessions else None
        if restored:
            self._active[operator_id] = restored
        self._emit("operator_session_restored", {"operator_id": operator_id[:40], "restored": bool(restored)})
        return {"accepted": True, "restored": bool(restored), "session": restored, "reversible": True}

    async def synchronize_session_state(self) -> dict[str, Any]:
        return {"accepted": True, "active": list(self._active.values()), "permission_aware": True}

    async def build_session_replay(self) -> dict[str, Any]:
        return {"accepted": True, "replay": self._store.sessions(limit=20), "lazy_hydration": True}

    def snapshot(self) -> dict[str, Any]:
        return {"active": list(self._active.values()), "sessions": len(self._store.sessions())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_sessions")
''')
w("operator_sessions/__init__.py", '''from odin_backend.core.operator_sessions.operator_sessions_runtime import OperatorSessionsRuntime

__all__ = ["OperatorSessionsRuntime"]
''')

w("shared_mission_control/shared_mission_control_runtime.py", '''"""Shared mission control runtime (Prompt 62)."""
from __future__ import annotations
from typing import Any


class SharedMissionControlRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._missions: dict[str, dict[str, Any]] = {}
        self._owner = "operator-local"

    async def create_shared_mission(self, *, mission_id: str = "shared-mission", owner: str = "operator-local") -> dict[str, Any]:
        if not getattr(self._app.settings, "shared_mission_control_enabled", False):
            return {"accepted": False, "reason": "shared_mission_control_disabled"}
        self._owner = owner
        self._missions[mission_id] = {"mission_id": mission_id, "owner": owner, "operators": [owner], "virtualized": True}
        if hasattr(self._app, "mission_command"):
            await self._app.mission_command.synchronize_objective_graph()
        self._emit("shared_mission_created", {"mission_id": mission_id[:40], "owner": owner[:40]})
        return {"accepted": True, "mission_id": mission_id, "owner": owner, "bounded": True}

    async def transfer_mission_control(self, *, mission_id: str = "shared-mission", operator_id: str = "operator-local") -> dict[str, Any]:
        mission = self._missions.setdefault(mission_id, {"mission_id": mission_id, "operators": []})
        mission["owner"] = operator_id
        self._owner = operator_id
        self._emit("mission_control_transferred", {"mission_id": mission_id[:40], "operator_id": operator_id[:40]})
        return {"accepted": True, "mission_id": mission_id, "owner": operator_id, "operator_controlled": True}

    async def synchronize_mission_state(self) -> dict[str, Any]:
        if hasattr(self._app, "unified_command_center"):
            await self._app.unified_command_center.synchronize_runtime_layers()
        return {"accepted": True, "missions": list(self._missions.values()), "transparent": True}

    async def generate_team_pressure_map(self) -> dict[str, Any]:
        pressures = {m["owner"]: 0.4 for m in self._missions.values()} or {self._owner: 0.4}
        return {"accepted": True, "pressure_map": pressures, "operator_visible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"missions": list(self._missions.values()), "owner": self._owner}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="shared_mission_control")
''')
w("shared_mission_control/__init__.py", '''from odin_backend.core.shared_mission_control.shared_mission_control_runtime import SharedMissionControlRuntime

__all__ = ["SharedMissionControlRuntime"]
''')

w("delegation_engine/delegation_engine_runtime.py", '''"""Delegation engine runtime (Prompt 62)."""
from __future__ import annotations
from typing import Any


class DelegationEngineRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._delegations: dict[str, dict[str, Any]] = {}
        self._replay_loops = 0

    async def delegate_execution(self, *, task_id: str = "task-local", operator_id: str = "operator-local") -> dict[str, Any]:
        if not getattr(self._app.settings, "delegation_engine_enabled", False):
            return {"accepted": False, "reason": "delegation_engine_disabled"}
        authority = await self.validate_operator_authority(operator_id=operator_id)
        if not authority.get("valid"):
            return {"accepted": False, "reason": "authority_denied", "approval_gated": True}
        self._delegations[task_id] = {"task_id": task_id, "operator_id": operator_id, "status": "delegated"}
        self._emit("delegation_chain_created", {"task_id": task_id[:40], "operator_id": operator_id[:40]})
        return {"accepted": True, "task_id": task_id, "operator_id": operator_id, "approval_gated": True}

    async def revoke_delegation(self, *, task_id: str = "task-local") -> dict[str, Any]:
        delegation = self._delegations.get(task_id)
        if delegation:
            delegation["status"] = "revoked"
        return {"accepted": True, "task_id": task_id, "revoked": bool(delegation), "reversible": True}

    async def validate_operator_authority(self, *, operator_id: str = "operator-local") -> dict[str, Any]:
        valid = True
        if hasattr(self._app, "operator_sessions"):
            state = await self._app.operator_sessions.synchronize_session_state()
            active = state.get("active", [])
            valid = not active or any(s.get("operator_id") == operator_id or s.get("approval_authority") for s in active)
        self._emit("delegation_authority_validated", {"operator_id": operator_id[:40], "valid": valid})
        return {"accepted": True, "valid": valid, "permission_aware": True}

    async def replay_delegation_chain(self) -> dict[str, Any]:
        if self._replay_loops > 40:
            return {"accepted": False, "reason": "delegation_replay_bounded"}
        self._replay_loops += 1
        return {"accepted": True, "delegations": list(self._delegations.values()), "lazy_hydration": True}

    def snapshot(self) -> dict[str, Any]:
        return {"delegations": list(self._delegations.values()), "replay_loops": self._replay_loops}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="delegation_engine")
''')
w("delegation_engine/__init__.py", '''from odin_backend.core.delegation_engine.delegation_engine_runtime import DelegationEngineRuntime

__all__ = ["DelegationEngineRuntime"]
''')

w("team_coordination/team_coordination_runtime.py", '''"""Team coordination runtime (Prompt 62)."""
from __future__ import annotations
from typing import Any


class TeamCoordinationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._pressure = 0.45
        self._noise_suppressed = False
        self._rebalance_count = 0

    async def estimate_team_pressure(self) -> dict[str, Any]:
        if hasattr(self._app, "shared_mission_control"):
            await self._app.shared_mission_control.generate_team_pressure_map()
        self._emit("team_pressure_updated", {"pressure": self._pressure})
        return {"accepted": True, "pressure": round(self._pressure, 2), "operator_visible": True}

    async def rebalance_team_attention(self) -> dict[str, Any]:
        if self._rebalance_count > 48:
            return {"accepted": False, "reason": "team_rebalance_bounded"}
        self._rebalance_count += 1
        self._pressure = max(0.1, self._pressure - 0.04)
        self._emit("team_attention_rebalanced", {"pressure": self._pressure})
        return {"accepted": True, "pressure": round(self._pressure, 2), "bounded": True}

    async def suppress_cross_operator_noise(self) -> dict[str, Any]:
        self._noise_suppressed = True
        self._emit("cross_operator_noise_suppressed", {"suppressed": True})
        return {"accepted": True, "suppressed": True, "low_power": True}

    async def generate_coordination_snapshot(self) -> dict[str, Any]:
        return {"accepted": True, "snapshot": self.snapshot(), "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"pressure": self._pressure, "noise_suppressed": self._noise_suppressed, "rebalance_count": self._rebalance_count}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="team_coordination")
''')
w("team_coordination/__init__.py", '''from odin_backend.core.team_coordination.team_coordination_runtime import TeamCoordinationRuntime

__all__ = ["TeamCoordinationRuntime"]
''')

w("collaborative_recovery/collaborative_recovery_runtime.py", '''"""Collaborative recovery runtime (Prompt 62)."""
from __future__ import annotations
from typing import Any


class CollaborativeRecoveryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._requests: list[dict[str, Any]] = []
        self._authorized: list[str] = []
        self._rollback_generated = False

    async def request_team_recovery(self, *, mission_id: str = "shared-mission") -> dict[str, Any]:
        if not getattr(self._app.settings, "collaborative_recovery_enabled", False):
            return {"accepted": False, "reason": "collaborative_recovery_disabled"}
        req = {"mission_id": mission_id, "status": "pending"}
        self._requests.append(req)
        if hasattr(self._app, "operator_veto"):
            await self._app.operator_veto.request_recovery_approval(path=f"team:{mission_id}", risk=0.4)
        self._emit("collaborative_recovery_requested", {"mission_id": mission_id[:40]})
        return {"accepted": True, "mission_id": mission_id, "approval_gated": True}

    async def authorize_shared_recovery(self, *, mission_id: str = "shared-mission") -> dict[str, Any]:
        if hasattr(self._app, "operator_veto"):
            auth = await self._app.operator_veto.authorize_recovery_chain(path=f"team:{mission_id}")
            if not auth.get("authorized"):
                return {"accepted": False, "reason": "shared_recovery_not_authorized"}
        self._authorized.append(mission_id)
        self._emit("shared_recovery_authorized", {"mission_id": mission_id[:40]})
        return {"accepted": True, "authorized": True, "mission_id": mission_id, "operator_supervised": True}

    async def build_collaborative_rollback(self, *, mission_id: str = "shared-mission") -> dict[str, Any]:
        if hasattr(self._app, "rollback_intelligence"):
            await self._app.rollback_intelligence.generate_rollback_graph()
        self._rollback_generated = True
        self._emit("collaborative_rollback_generated", {"mission_id": mission_id[:40]})
        return {"accepted": True, "mission_id": mission_id, "rollback_generated": True, "reversible": True}

    async def synchronize_recovery_state(self) -> dict[str, Any]:
        if hasattr(self._app, "continuity_recovery"):
            await self._app.continuity_recovery.recover_mission_continuity()
        self._emit("shared_continuity_restored", {"requests": len(self._requests)})
        return {"accepted": True, "synchronized": True, "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"requests": self._requests, "authorized": self._authorized, "rollback_generated": self._rollback_generated}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="collaborative_recovery")
''')
w("collaborative_recovery/__init__.py", '''from odin_backend.core.collaborative_recovery.collaborative_recovery_runtime import CollaborativeRecoveryRuntime

__all__ = ["CollaborativeRecoveryRuntime"]
''')

print("bootstrap_p62_core complete")

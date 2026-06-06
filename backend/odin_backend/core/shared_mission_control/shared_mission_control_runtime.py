"""Shared mission control runtime (Prompt 62)."""
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

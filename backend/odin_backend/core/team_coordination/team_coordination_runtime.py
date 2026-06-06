"""Team coordination runtime (Prompt 62)."""
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

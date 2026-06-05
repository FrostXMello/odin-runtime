"""Runtime stability guardian orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.stability.crash_recovery import recover_from_crash
from odin_backend.core.stability.degraded_operation import activate_degraded
from odin_backend.core.stability.emergency_recovery import emergency_recover
from odin_backend.core.stability.health_supervisor import HealthSupervisor
from odin_backend.core.stability.runtime_repair import repair_runtime
from odin_backend.core.stability.state_checkpointing import StateCheckpointing
from odin_backend.core.stability.watchdog_runtime import WatchdogRuntime


class RuntimeGuardian:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._health = HealthSupervisor()
        self._watchdog = WatchdogRuntime()
        self._checkpoints = StateCheckpointing()
        self._degraded = False
        self._mode = "normal"
        self._recoveries = 0

    async def connect(self) -> None:
        if getattr(self._app.settings, "runtime_guardian_enabled", False):
            self._watchdog.heartbeat("runtime_guardian")

    async def disconnect(self) -> None:
        pass

    async def supervise(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_guardian_enabled", False):
            return {"accepted": False, "reason": "runtime_guardian_disabled"}
        pressure = "normal"
        if hasattr(self._app, "resource_optimization"):
            snap = self._app.resource_optimization.snapshot()
            pressure = snap.get("mode_config", {}).get("pressure", "normal")
        stalled = self._watchdog.detect_stalled()
        health = self._health.evaluate(loop_age_s=0.0, memory_pressure=pressure, stalled_loops=len(stalled))
        actions: list[str] = []
        if stalled:
            repair = await repair_runtime(self._app, reason="stalled_loops")
            actions.append("runtime_repaired")
            self._emit("watchdog_triggered", {"stalled": stalled, "repair": repair})
            self._emit("runtime_repaired", repair)
        if health["status"] == "degraded" and not self._degraded:
            degraded = activate_degraded(reason="health_supervisor", level="degraded")
            self._degraded = True
            self._mode = degraded["mode"]
            if hasattr(self._app, "resource_optimization"):
                self._app.resource_optimization.set_mode("degraded")
            self._emit("degraded_mode_enabled", degraded)
            actions.append("degraded_mode")
        ckpt = self._checkpoints.create(label="supervise", state={"health": health, "mode": self._mode})
        return {"accepted": True, "health": health, "stalled": stalled, "actions": actions, "checkpoint_id": ckpt["id"]}

    async def recover(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_guardian_enabled", False):
            return {"accepted": False, "reason": "runtime_guardian_disabled"}
        result = await recover_from_crash(self._app)
        self._recoveries += 1
        self._emit("runtime_recovered", result)
        return {"accepted": True, **result}

    async def emergency(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_guardian_enabled", False):
            return {"accepted": False, "reason": "runtime_guardian_disabled"}
        result = await emergency_recover(self._app)
        self._recoveries += 1
        self._emit("runtime_recovered", result)
        return {"accepted": True, **result}

    async def checkpoint(self, *, label: str = "manual") -> dict[str, Any]:
        state = self.snapshot()
        ckpt = self._checkpoints.create(label=label, state=state)
        return ckpt

    def snapshot(self) -> dict[str, Any]:
        return {
            "mode": self._mode,
            "degraded": self._degraded,
            "recoveries": self._recoveries,
            "health": self._health.history(1)[-1] if self._health.history(1) else {},
            "watchdog": self._watchdog.snapshot(),
            "checkpoints": len(self._checkpoints.list_all()),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="runtime_guardian")

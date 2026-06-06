"""Replay orchestration runtime (Prompt 63)."""
from __future__ import annotations
from typing import Any

MAX_REPLAY_LOOPS = 56


class ReplayOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._window: dict[str, Any] | None = None
        self._checkpoints: list[dict[str, Any]] = []
        self._density = 1.0
        self._replay_loops = 0

    async def initialize_replay_window(self, *, window_id: str = "replay-window") -> dict[str, Any]:
        if not getattr(self._app.settings, "replay_orchestration_enabled", False):
            return {"accepted": False, "reason": "replay_orchestration_disabled"}
        if hasattr(self._app, "operator_veto"):
            await self._app.operator_veto.request_recovery_approval(path=f"replay:{window_id}", risk=0.3)
        self._window = {"window_id": window_id, "bounded": True, "supervised": True}
        if hasattr(self._app, "continuity_recovery"):
            await self._app.continuity_recovery.replay_continuity_window()
        self._emit("replay_window_initialized", {"window_id": window_id[:40]})
        return {
            "accepted": True,
            "window": self._window,
            "approval_gated": True,
            "transparent": True,
        }

    async def replay_cognition_timeline(self) -> dict[str, Any]:
        if self._replay_loops >= MAX_REPLAY_LOOPS:
            return {"accepted": False, "reason": "replay_loop_bounded"}
        self._replay_loops += 1
        if hasattr(self._app, "live_cognition_timeline"):
            await self._app.live_cognition_timeline.replay_cognition_window()
        if hasattr(self._app, "mission_continuity"):
            await self._app.mission_continuity.estimate_continuity_health()
        self._emit("cognition_timeline_replayed", {"loops": self._replay_loops})
        return {
            "accepted": True,
            "replayed": True,
            "loops": self._replay_loops,
            "lazy_hydration": True,
            "supervised": True,
        }

    async def checkpoint_replay_state(self) -> dict[str, Any]:
        checkpoint = {"frame": self._replay_loops, "density": self._density, "window": self._window}
        self._checkpoints.append(checkpoint)
        if len(self._checkpoints) > 40:
            self._checkpoints = self._checkpoints[-40:]
        self._emit("replay_state_checkpointed", {"checkpoints": len(self._checkpoints)})
        return {"accepted": True, "checkpoint": checkpoint, "reversible": True}

    async def throttle_replay_density(self) -> dict[str, Any]:
        mode = getattr(self._app.settings, "replay_density", "adaptive")
        self._density = max(0.2, self._density - 0.05) if mode == "adaptive" else self._density
        self._emit("replay_density_throttled", {"density": self._density})
        return {
            "accepted": True,
            "density": round(self._density, 2),
            "mode": mode,
            "low_power": self._density < 0.5,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "window": self._window,
            "checkpoints": len(self._checkpoints),
            "density": self._density,
            "replay_loops": self._replay_loops,
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="replay_orchestration")

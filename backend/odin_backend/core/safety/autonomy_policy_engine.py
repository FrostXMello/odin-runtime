"""Autonomy safety — bounded execution and throttles."""

from __future__ import annotations

from typing import Any

from odin_backend.core.autonomy.autonomy_policy import AutonomyPermissionMode
from odin_backend.core.safety.loop_detection import LoopDetector
from odin_backend.core.safety.throttle import MissionThrottle


class AutonomyPolicyEngine:
    def __init__(self, app: Any) -> None:
        self._app = app
        max_missions = getattr(app.settings, "autonomy_mission_budget_per_hour", 5)
        self._throttle = MissionThrottle(max_per_hour=max_missions)
        self._loop_detector = LoopDetector()
        self._interventions: list[dict] = []
        self._depth = 0

    def allow_cycle(self) -> bool:
        count = self._loop_detector.record()
        if self._loop_detector.is_runaway():
            self._intervene("loop_detected", {"events_in_window": count})
            return False
        loop = getattr(self._app, "autonomous_loop", None)
        if loop and loop.state.run_state.value == "paused":
            return False
        return True

    def allow_mission_spawn(self) -> bool:
        if not self._throttle.allow():
            self._intervene("mission_throttle", {"reason": "hourly_budget_exceeded"})
            return False
        mode = getattr(self._app.settings, "autonomy_mode", "supervised")
        if mode == AutonomyPermissionMode.OBSERVE_ONLY.value:
            return False
        return True

    def record_mission_spawned(self) -> None:
        self._throttle.record()

    def require_approval(self, objective: str) -> bool:
        mode = getattr(self._app.settings, "autonomy_mode", "supervised")
        if mode in (AutonomyPermissionMode.FULLY_LOCAL_AUTONOMOUS.value,):
            return False
        if mode == AutonomyPermissionMode.RESEARCH_ONLY.value:
            return "research" not in objective.lower()
        return True

    def _intervene(self, kind: str, payload: dict) -> None:
        self._interventions.append({"kind": kind, **payload})
        if len(self._interventions) > 50:
            self._interventions = self._interventions[-50:]
        loop = getattr(self._app, "autonomous_loop", None)
        if loop:
            loop.metrics.safety_interventions += 1
        obs = getattr(self._app, "observability", None)
        if obs:
            from odin_backend.core.observability.events import TraceEventKind

            try:
                kind_enum = TraceEventKind("safety_intervention" if kind != "loop_detected" else "loop_detected")
            except ValueError:
                return
            obs.tracer.record(kind_enum, message=kind, payload=payload, component="autonomy_safety")

    def violations(self) -> list[dict]:
        return list(self._interventions)

    def snapshot(self) -> dict:
        return {
            "interventions": self._interventions[-10:],
            "throttle_remaining": max(0, self._throttle._max - len(self._throttle._timestamps)),
        }

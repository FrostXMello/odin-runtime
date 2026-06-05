"""Society safety and governance."""

from __future__ import annotations

from typing import Any


class SocietyGovernance:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._debate_depth: dict[str, int] = {}
        self._message_counts: dict[str, int] = {}

    def allow_spawn(self, current_count: int) -> tuple[bool, str]:
        if not getattr(self._app.settings, "agent_society_enabled", False):
            return False, "agent_society_disabled"
        limit = getattr(self._app.settings, "agent_society_max_agents", 12)
        if current_count >= limit:
            return False, "population_limit"
        if getattr(self._app, "action_runtime", None) and self._app.action_runtime.emergency_stopped:
            return False, "emergency_stop"
        return True, "ok"

    def allow_message(self, agent_id: str) -> bool:
        limit = getattr(self._app.settings, "agent_message_rate_per_minute", 30)
        self._message_counts[agent_id] = self._message_counts.get(agent_id, 0) + 1
        return self._message_counts[agent_id] <= limit

    def track_debate(self, session_id: str) -> bool:
        depth = self._debate_depth.get(session_id, 0) + 1
        self._debate_depth[session_id] = depth
        return depth <= getattr(self._app.settings, "agent_debate_max_depth", 8)

    def snapshot(self) -> dict[str, Any]:
        return {
            "max_agents": getattr(self._app.settings, "agent_society_max_agents", 12),
            "debate_sessions_tracked": len(self._debate_depth),
        }

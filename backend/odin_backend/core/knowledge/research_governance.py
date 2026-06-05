"""Research safety and governance."""

from __future__ import annotations

from typing import Any

_HARMFUL = ("exploit", "weapon", "malware", "illegal")


class ResearchGovernance:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._budget_used = 0

    def allow_research(self, topic: str) -> bool:
        if not getattr(self._app.settings, "research_fabric_enabled", False):
            return False
        lower = topic.lower()
        if any(h in lower for h in _HARMFUL):
            return False
        budget = getattr(self._app.settings, "research_budget_per_hour", 10)
        if self._budget_used >= budget:
            return False
        if getattr(self._app, "action_runtime", None) and self._app.action_runtime.emergency_stopped:
            return False
        self._budget_used += 1
        return True

    def reset_budget(self) -> None:
        self._budget_used = 0

    def snapshot(self) -> dict[str, Any]:
        return {
            "budget_used": self._budget_used,
            "budget_limit": getattr(self._app.settings, "research_budget_per_hour", 10),
            "web_read_only": True,
        }

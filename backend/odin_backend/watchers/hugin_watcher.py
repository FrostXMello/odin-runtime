"""HUGIN watcher — AI news, trends, GitHub (monitor only)."""

from typing import Any

from odin_backend.events.bus import EventBus
from odin_backend.models.task import AgentId
from odin_backend.watchers.base import BaseWatcher


class HuginWatcher(BaseWatcher):
    agent_id = AgentId.HUGIN
    name = "hugin_monitor"

    def __init__(self, event_bus: EventBus, interval_seconds: int = 300) -> None:
        super().__init__(event_bus)
        self.interval_seconds = interval_seconds
        self._topics = ["AI agents", "LLM orchestration", "open source AI"]

    async def observe(self) -> list[dict[str, Any]]:
        insights = []
        for topic in self._topics:
            insights.append({
                "type": "trend_watch",
                "topic": topic,
                "summary": f"Monitoring trends for: {topic}",
                "recommendation": f"Consider reviewing latest developments in {topic}.",
                "action": "none",
            })
        return insights

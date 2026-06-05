"""FAFNIR watcher — market monitoring (insights only)."""

from typing import Any

from odin_backend.events.bus import EventBus
from odin_backend.models.task import AgentId
from odin_backend.watchers.base import BaseWatcher


class FafnirWatcher(BaseWatcher):
    agent_id = AgentId.FAFNIR
    name = "fafnir_market"

    def __init__(self, event_bus: EventBus, interval_seconds: int = 120) -> None:
        super().__init__(event_bus)
        self.interval_seconds = interval_seconds
        self._symbols = ["SPY", "BTC", "ETH"]

    async def observe(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "market_watch",
                "symbol": sym,
                "summary": f"Monitoring {sym} — configure market data API for live quotes.",
                "recommendation": f"Review {sym} position if thresholds configured.",
                "action": "none",
            }
            for sym in self._symbols
        ]

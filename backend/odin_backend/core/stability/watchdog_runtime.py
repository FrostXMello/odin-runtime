"""Watchdog for stalled runtime loops."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class WatchdogRuntime:
    def __init__(self, *, stall_threshold_s: float = 120.0) -> None:
        self._threshold = stall_threshold_s
        self._heartbeats: dict[str, str] = {}
        self._triggers: list[dict[str, Any]] = []

    def heartbeat(self, component: str) -> None:
        self._heartbeats[component] = datetime.now(timezone.utc).isoformat()

    def detect_stalled(self, now_ts: float | None = None) -> list[str]:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc) if now_ts is None else datetime.fromtimestamp(now_ts, tz=timezone.utc)
        stalled: list[str] = []
        for component, ts in self._heartbeats.items():
            try:
                last = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                age = (now - last).total_seconds()
                if age > self._threshold:
                    stalled.append(component)
            except ValueError:
                stalled.append(component)
        if stalled:
            self._triggers.append({"stalled": stalled, "at": now.isoformat()})
        return stalled

    def snapshot(self) -> dict[str, Any]:
        return {"heartbeats": dict(self._heartbeats), "triggers": self._triggers[-10:]}

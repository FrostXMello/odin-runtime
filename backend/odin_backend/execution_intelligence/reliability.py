"""Tool reliability scoring."""

from typing import Any

from pydantic import BaseModel, Field


class ToolReliabilityScore(BaseModel):
    tool_name: str
    success_rate: float = 1.0
    avg_latency_ms: float = 0.0
    retry_count: int = 0
    domain: str = "general"
    sample_size: int = 0


class ToolReliabilityTracker:
    def __init__(self) -> None:
        self._stats: dict[str, dict[str, Any]] = {}

    def record(
        self,
        tool_name: str,
        *,
        success: bool,
        latency_ms: float = 0.0,
        domain: str = "general",
    ) -> None:
        key = f"{tool_name}:{domain}"
        if key not in self._stats:
            self._stats[key] = {
                "successes": 0,
                "failures": 0,
                "retries": 0,
                "latency_sum": 0.0,
                "tool_name": tool_name,
                "domain": domain,
            }
        s = self._stats[key]
        if success:
            s["successes"] += 1
        else:
            s["failures"] += 1
        s["latency_sum"] += latency_ms

    def record_retry(self, tool_name: str, domain: str = "general") -> None:
        key = f"{tool_name}:{domain}"
        if key in self._stats:
            self._stats[key]["retries"] += 1

    def score(self, tool_name: str, domain: str = "general") -> ToolReliabilityScore:
        key = f"{tool_name}:{domain}"
        s = self._stats.get(key)
        if not s:
            return ToolReliabilityScore(tool_name=tool_name, domain=domain)
        total = s["successes"] + s["failures"]
        rate = s["successes"] / total if total else 1.0
        avg_lat = s["latency_sum"] / total if total else 0.0
        return ToolReliabilityScore(
            tool_name=tool_name,
            success_rate=round(rate, 3),
            avg_latency_ms=round(avg_lat, 1),
            retry_count=s["retries"],
            domain=domain,
            sample_size=total,
        )

    def all_scores(self) -> list[ToolReliabilityScore]:
        seen: set[str] = set()
        out: list[ToolReliabilityScore] = []
        for key in self._stats:
            tool = self._stats[key]["tool_name"]
            domain = self._stats[key]["domain"]
            if tool not in seen:
                out.append(self.score(tool, domain))
                seen.add(tool)
        return out

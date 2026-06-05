"""Runtime metrics — latency, tokens, tool times, agent uptime."""

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MetricPoint(BaseModel):
    name: str
    value: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: dict[str, str] = Field(default_factory=dict)


class MetricsCollector:
    def __init__(self) -> None:
        self._counters: dict[str, float] = defaultdict(float)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._recent: list[MetricPoint] = []

    def increment(self, name: str, value: float = 1.0, **tags: str) -> None:
        key = self._key(name, tags)
        self._counters[key] += value
        self._record(name, value, tags)

    def record_latency(self, name: str, seconds: float, **tags: str) -> None:
        key = self._key(name, tags)
        self._histograms[key].append(seconds)
        if len(self._histograms[key]) > 1000:
            self._histograms[key] = self._histograms[key][-500:]
        self._record(name, seconds, tags)

    def record_workflow(self, status: str, _: str = "") -> None:
        self.increment("workflow.completed" if status == "completed" else "workflow.failed", tags={"status": status})

    def record_tool_execution(self, tool: str, seconds: float, success: bool) -> None:
        self.record_latency("tool.execution", seconds, tool=tool, success=str(success))
        self.increment("tool.executions", tags={"tool": tool, "success": str(success)})

    def record_token_usage(self, tokens: int, model: str = "default") -> None:
        self.increment("llm.tokens", float(tokens), model=model)

    def record_memory_retrieval(self) -> None:
        self.increment("memory.retrievals")

    def _key(self, name: str, tags: dict) -> str:
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}|{tag_str}" if tag_str else name

    def _record(self, name: str, value: float, tags: dict) -> None:
        self._recent.append(MetricPoint(name=name, value=value, tags={k: str(v) for k, v in tags.items()}))
        if len(self._recent) > 2000:
            self._recent = self._recent[-1000:]

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "recent": [m.model_dump(mode="json") for m in self._recent[-50:]],
            "latency_avg": {
                k: sum(v) / len(v) if v else 0
                for k, v in self._histograms.items()
            },
        }

"""Execution engine metrics."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExecutionMetrics:
    total_started: int = 0
    total_completed: int = 0
    total_failed: int = 0
    total_cancelled: int = 0
    total_timed_out: int = 0
    total_retries: int = 0
    active_count: int = 0
    throughput_per_minute: float = 0.0
    _recent_completions: list[float] = field(default_factory=list)

    def record_completion(self, *, ts: float) -> None:
        self.total_completed += 1
        self._recent_completions.append(ts)
        self._recent_completions = self._recent_completions[-120:]
        if len(self._recent_completions) >= 2:
            window = self._recent_completions[-1] - self._recent_completions[0]
            if window > 0:
                self.throughput_per_minute = (len(self._recent_completions) - 1) / window * 60

    def snapshot(self) -> dict:
        return {
            "total_started": self.total_started,
            "total_completed": self.total_completed,
            "total_failed": self.total_failed,
            "total_cancelled": self.total_cancelled,
            "total_timed_out": self.total_timed_out,
            "total_retries": self.total_retries,
            "active_count": self.active_count,
            "throughput_per_minute": round(self.throughput_per_minute, 2),
        }

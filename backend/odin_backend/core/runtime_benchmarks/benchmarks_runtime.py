"""Continuous runtime benchmarking."""
from __future__ import annotations
import time
from typing import Any

from odin_backend.core.runtime_benchmarks.autonomy_benchmarks import run as autonomy_bench
from odin_backend.core.runtime_benchmarks.benchmark_scheduler import schedule
from odin_backend.core.runtime_benchmarks.cognition_benchmarks import run as cognition_bench
from odin_backend.core.runtime_benchmarks.engineering_benchmarks import run as engineering_bench
from odin_backend.core.runtime_benchmarks.latency_benchmarks import run as latency_bench
from odin_backend.core.runtime_benchmarks.memory_benchmarks import run as memory_bench
from odin_backend.core.runtime_benchmarks.reasoning_benchmarks import run as reasoning_bench


class RuntimeBenchmarksRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._history: list[dict] = []

    async def run_suite(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_benchmarks_enabled", False):
            return {"accepted": False, "reason": "runtime_benchmarks_disabled"}
        report = {
            "cognition": cognition_bench(),
            "reasoning": reasoning_bench(),
            "latency": latency_bench(),
            "memory": memory_bench(),
            "engineering": engineering_bench(),
            "autonomy": autonomy_bench(),
            "ts": time.time(),
        }
        self._history.append(report)
        if len(self._history) >= 2:
            prev = self._history[-2]["latency"]["p95_ms"]
            curr = report["latency"]["p95_ms"]
            if curr > prev * 1.15:
                self._emit("regression_detected", {"metric": "latency_p95", "prev": prev, "curr": curr})
        self._emit("benchmark_completed", {"suites": 6})
        return {"accepted": True, "report": report, "history_len": len(self._history)}

    async def history(self) -> dict[str, Any]:
        return {"accepted": True, "history": self._history[-20:]}

    def snapshot(self) -> dict[str, Any]:
        return {"history_len": len(self._history), "schedule": schedule()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="runtime_benchmarks")

"""Recursion guard — lineage tracking, depth limits, loop suppression."""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from odin_backend.core.bus.signals import Signal, SignalOrigin
from odin_backend.core.runtime.recursion_guard.models import (
    RecursionGuardDecision,
    RecursionGuardMetrics,
    RecursionGuardResult,
    SuppressedLoopRecord,
)
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class RecursionGuard:
    """
    Detects recursive cognitive signal chains.

    Tracks recent chain fingerprints within a sliding window and suppresses
    duplicates that exceed configured thresholds.
    """

    def __init__(
        self,
        *,
        max_depth: int = 12,
        loop_window_seconds: float = 5.0,
        max_repeats: int = 6,
        max_trace_entries: int = 200,
        max_suppressed_records: int = 50,
    ) -> None:
        self._max_depth = max_depth
        self._loop_window = loop_window_seconds
        self._max_repeats = max_repeats
        self._depth = 0
        self._lineage: deque[str] = deque(maxlen=max_trace_entries)
        self._chain_hits: dict[str, deque[float]] = {}
        self._suppressed: deque[SuppressedLoopRecord] = deque(maxlen=max_suppressed_records)
        self._metrics = RecursionGuardMetrics()
        self._kernel_processed = 0
        self._kernel_window_start = time.monotonic()

    @property
    def metrics(self) -> RecursionGuardMetrics:
        self._refresh_loop_health()
        self._metrics.active_signal_chains = len(self._chain_hits)
        self._metrics.active_chains = [
            {"chain_key": k, "hits": len(v)} for k, v in list(self._chain_hits.items())[:20]
        ]
        self._metrics.suppressed_loops = [r.model_dump() for r in list(self._suppressed)[-20:]]
        return self._metrics.model_copy(deep=True)

    @property
    def current_depth(self) -> int:
        return self._depth

    def evaluate(self, signal: Signal, *, eligible_for_kernel: bool) -> RecursionGuardResult:
        if not eligible_for_kernel:
            return RecursionGuardResult(
                decision=RecursionGuardDecision.ALLOW,
                reason="not_kernel_eligible",
                chain_key=self._chain_key(signal),
            )

        chain_key = self._chain_key(signal)
        now = time.monotonic()
        self._record_hit(chain_key, now)
        repeats = self._count_in_window(chain_key, now)

        trace = list(self._lineage)[-10:]
        trace.append(chain_key)

        if self._depth >= self._max_depth:
            self._record_suppression(chain_key, repeats, signal)
            return RecursionGuardResult(
                decision=RecursionGuardDecision.SUPPRESS,
                reason="max_recursion_depth",
                chain_key=chain_key,
                depth=self._depth,
                repeat_count=repeats,
                trace=trace,
            )

        if repeats > self._max_repeats:
            self._record_suppression(chain_key, repeats, signal)
            if repeats > self._max_repeats * 2:
                self._metrics.escalated_signal_count += 1
                self._metrics.recursion_events_detected += 1
                logger.warning(
                    "recursion_guard_escalate",
                    chain_key=chain_key,
                    repeats=repeats,
                )
                return RecursionGuardResult(
                    decision=RecursionGuardDecision.ESCALATE,
                    reason="loop_threshold_exceeded",
                    chain_key=chain_key,
                    depth=self._depth,
                    repeat_count=repeats,
                    trace=trace,
                )
            self._metrics.recursion_events_detected += 1
            self._metrics.suppressed_signal_count += 1
            logger.warning(
                "recursion_guard_suppress",
                chain_key=chain_key,
                repeats=repeats,
            )
            return RecursionGuardResult(
                decision=RecursionGuardDecision.SUPPRESS,
                reason="duplicate_chain",
                chain_key=chain_key,
                depth=self._depth,
                repeat_count=repeats,
                trace=trace,
            )

        return RecursionGuardResult(
            decision=RecursionGuardDecision.ALLOW,
            chain_key=chain_key,
            depth=self._depth,
            repeat_count=repeats,
            trace=trace,
        )

    def enter_kernel(self, signal: Signal) -> None:
        self._depth += 1
        self._lineage.append(self._chain_key(signal))

    def exit_kernel(self) -> None:
        self._depth = max(0, self._depth - 1)

    def record_kernel_processed(self) -> None:
        self._kernel_processed += 1
        elapsed = time.monotonic() - self._kernel_window_start
        if elapsed >= 1.0:
            self._metrics.kernel_processing_rate = self._kernel_processed / elapsed
            self._kernel_processed = 0
            self._kernel_window_start = time.monotonic()

    def _chain_key(self, signal: Signal) -> str:
        corr = signal.correlation_id or signal.workflow_id or signal.task_id or "-"
        return f"{signal.origin.value}:{signal.type}:{corr}"

    def _record_hit(self, chain_key: str, now: float) -> None:
        hits = self._chain_hits.setdefault(chain_key, deque(maxlen=64))
        hits.append(now)
        self._prune_chain(chain_key, now)

    def _count_in_window(self, chain_key: str, now: float) -> int:
        hits = self._chain_hits.get(chain_key)
        if not hits:
            return 0
        cutoff = now - self._loop_window
        return sum(1 for t in hits if t >= cutoff)

    def _prune_chain(self, chain_key: str, now: float) -> None:
        hits = self._chain_hits.get(chain_key)
        if not hits:
            return
        cutoff = now - self._loop_window
        while hits and hits[0] < cutoff:
            hits.popleft()
        if not hits:
            self._chain_hits.pop(chain_key, None)

    def _record_suppression(self, chain_key: str, repeats: int, signal: Signal) -> None:
        now_ms = time.monotonic() * 1000
        self._suppressed.append(
            SuppressedLoopRecord(
                chain_key=chain_key,
                repeat_count=repeats,
                first_seen_ms=now_ms,
                last_seen_ms=now_ms,
                sample_types=[signal.type],
            )
        )

    def _refresh_loop_health(self) -> None:
        suppressed = self._metrics.suppressed_signal_count
        escalated = self._metrics.escalated_signal_count
        if escalated >= 3 or suppressed >= 20:
            self._metrics.runtime_loop_health = "critical"
        elif suppressed >= 5 or self._depth > self._max_depth // 2:
            self._metrics.runtime_loop_health = "degraded"
        else:
            self._metrics.runtime_loop_health = "healthy"

    def snapshot(self) -> dict[str, Any]:
        return self.metrics.model_dump()

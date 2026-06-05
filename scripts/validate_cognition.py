#!/usr/bin/env python3
"""Phase 2 — ODIN cognitive cycle validation."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validator_lib.client import ValidatorClient
from validator_lib.console import ColoredConsole
from validator_lib.logging_config import setup_logging
from validator_lib.results import CheckResult, PhaseResult, ValidationStatus

DEFAULT_OBJECTIVE = "Analyze runtime stability and summarize active systems"
COGNITIVE_CYCLE_PATH = "/api/v1/live/cognitive-cycle"
KERNEL_STATE_PATH = "/api/v1/kernel/state"
RECURSION_PATH = "/api/v1/runtime/recursion"


def run_phase(
    base_url: str,
    *,
    objective: str = DEFAULT_OBJECTIVE,
    timeout: float = 120.0,
    retries: int = 2,
) -> PhaseResult:
    client = ValidatorClient(base_url, timeout=timeout, retries=retries)
    phase = PhaseResult(phase="Cognitive Cycle")
    t0 = time.monotonic()

    if not client.health_ping():
        phase.add(CheckResult("api_reachable", ValidationStatus.FAIL, "API not reachable"))
        phase.duration_seconds = time.monotonic() - t0
        return phase

    before_code, before_state, _ = client.get_json(KERNEL_STATE_PATH)
    before_signals = 0
    if isinstance(before_state, dict):
        before_signals = int(before_state.get("signal_count", 0))

    code, result, err = client.post_json(
        COGNITIVE_CYCLE_PATH,
        {"objective": objective},
        timeout=timeout,
    )

    if err or code == 0:
        phase.add(
            CheckResult(
                "cognitive_cycle_execute",
                ValidationStatus.FAIL,
                f"request failed: {err}",
            )
        )
        phase.duration_seconds = time.monotonic() - t0
        return phase

    if code >= 500:
        err_text = (err or str(result))[:300]
        if "recursion" in err_text.lower() or "maximum recursion" in err_text.lower():
            phase.add(
                CheckResult(
                    "no_recursion_errors",
                    ValidationStatus.FAIL,
                    "recursion detected in response",
                )
            )
        phase.add(
            CheckResult(
                "cognitive_cycle_execute",
                ValidationStatus.FAIL,
                f"HTTP {code}: {err_text}",
            )
        )
        phase.duration_seconds = time.monotonic() - t0
        return phase

    if code == 422:
        phase.add(
            CheckResult(
                "cognitive_cycle_execute",
                ValidationStatus.FAIL,
                f"validation error: {err}",
            )
        )
        phase.duration_seconds = time.monotonic() - t0
        return phase

    if code != 200:
        phase.add(
            CheckResult(
                "cognitive_cycle_execute",
                ValidationStatus.WARNING if code in (503, 504) else ValidationStatus.FAIL,
                f"HTTP {code}",
                {"body": str(result)[:200]},
            )
        )
    elif isinstance(result, dict):
        success = result.get("success", True)
        phase.add(
            CheckResult(
                "cognitive_cycle_execute",
                ValidationStatus.PASS if success else ValidationStatus.WARNING,
                f"success={success}",
                {
                    "model_used": result.get("model_used"),
                    "coherence_score": result.get("coherence_score"),
                    "governor_decision": result.get("governor_decision"),
                },
            )
        )
        gov = str(result.get("governor_decision", ""))
        if gov:
            phase.add(
                CheckResult(
                    "governor_path",
                    ValidationStatus.PASS,
                    f"decision={gov}",
                )
            )
        else:
            phase.add(
                CheckResult(
                    "governor_path",
                    ValidationStatus.WARNING,
                    "no governor_decision in cycle result",
                )
            )
        trace = result.get("execution_trace") or result.get("reasoning_trace") or []
        if trace or result.get("memory_updated"):
            phase.add(
                CheckResult(
                    "reasoning_pipeline",
                    ValidationStatus.PASS,
                    f"trace_steps={len(trace)}",
                )
            )
        else:
            phase.add(
                CheckResult(
                    "reasoning_pipeline",
                    ValidationStatus.WARNING,
                    "empty execution trace (fast path or read-only mode)",
                )
            )
    else:
        phase.add(
            CheckResult("cognitive_cycle_execute", ValidationStatus.FAIL, "non-object JSON response")
        )

    after_code, after_state, _ = client.get_json(KERNEL_STATE_PATH)
    if after_code == 200 and isinstance(after_state, dict):
        after_signals = int(after_state.get("signal_count", 0))
        if after_signals >= before_signals:
            phase.add(
                CheckResult(
                    "kernel_state_updates",
                    ValidationStatus.PASS,
                    f"signal_count {before_signals} -> {after_signals}",
                )
            )
        else:
            phase.add(
                CheckResult(
                    "kernel_state_updates",
                    ValidationStatus.WARNING,
                    f"signal_count unchanged ({after_signals})",
                )
            )
    else:
        phase.add(CheckResult("kernel_state_updates", ValidationStatus.FAIL, "cannot read kernel state"))

    r_code, r_data, _ = client.get_json(RECURSION_PATH)
    if r_code == 200 and isinstance(r_data, dict):
        depth = r_data.get("current_depth", 0)
        if int(depth) > 8:
            phase.add(
                CheckResult(
                    "no_recursion_errors",
                    ValidationStatus.WARNING,
                    f"high recursion depth: {depth}",
                )
            )
        else:
            phase.add(
                CheckResult(
                    "no_recursion_errors",
                    ValidationStatus.PASS,
                    f"guard depth={depth}",
                )
            )
    else:
        phase.add(
            CheckResult("no_recursion_errors", ValidationStatus.WARNING, "recursion endpoint unavailable")
        )

    phase.duration_seconds = time.monotonic() - t0
    phase.metadata = {"objective": objective[:120]}
    return phase


def main() -> int:
    parser = argparse.ArgumentParser(description="ODIN Phase 2 — Cognitive Cycle")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--objective", default=DEFAULT_OBJECTIVE)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(level=args.log_level)
    phase = run_phase(
        args.base_url,
        objective=args.objective,
        timeout=args.timeout,
        retries=args.retries,
    )
    console = ColoredConsole()

    if args.json:
        print(json.dumps(phase.to_dict(), indent=2))
    else:
        console.print_phase(phase)
        console.status_line(phase.status, f"Phase 2 result: {phase.status.value}")

    return 0 if phase.status == ValidationStatus.PASS else (1 if phase.status == ValidationStatus.FAIL else 2)


if __name__ == "__main__":
    raise SystemExit(main())

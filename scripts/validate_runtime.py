#!/usr/bin/env python3
"""Phase 1 — ODIN runtime stability validation."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validator_lib.client import ValidatorClient
from validator_lib.console import ColoredConsole
from validator_lib.logging_config import setup_logging
from validator_lib.results import CheckResult, PhaseResult, ValidationStatus

ENDPOINTS: list[tuple[str, str, list[str]]] = [
    ("/api/v1/runtime/health", "runtime_health", ["runtime_loop_health", "signal_count"]),
    ("/api/v1/runtime/signals", "runtime_signals", ["throughput", "kernel_queue"]),
    ("/api/v1/runtime/confidence", "runtime_confidence", ["global", "aggregate"]),
    ("/api/v1/perception/live", "perception_live", ["count", "perceptions"]),
    ("/api/v1/kernel/state", "kernel_state", ["signal_count", "current_focus"]),
]

RECURSION_PATH = "/api/v1/runtime/recursion"


def _check_endpoint(
    client: ValidatorClient,
    path: str,
    name: str,
    required_keys: list[str],
) -> CheckResult:
    code, data, err = client.get_json(path)
    if err or code == 0:
        return CheckResult(name, ValidationStatus.FAIL, f"unreachable: {err}")
    if code != 200:
        return CheckResult(name, ValidationStatus.FAIL, f"HTTP {code}", {"error": err})
    if not isinstance(data, dict):
        return CheckResult(name, ValidationStatus.FAIL, "expected JSON object")
    missing = [k for k in required_keys if k not in data]
    if missing:
        return CheckResult(
            name,
            ValidationStatus.WARNING,
            f"missing keys: {missing}",
            {"keys": list(data.keys())[:20]},
        )
    return CheckResult(name, ValidationStatus.PASS, f"HTTP {code}", {"keys": list(data.keys())[:15]})


def _check_recursion(client: ValidatorClient) -> CheckResult:
    code, data, err = client.get_json(RECURSION_PATH)
    if err or code != 200 or not isinstance(data, dict):
        return CheckResult("recursion_guard", ValidationStatus.FAIL, err or f"HTTP {code}")
    if not data.get("guard_enabled"):
        return CheckResult("recursion_guard", ValidationStatus.WARNING, "guard not enabled on bus")
    metrics = data.get("metrics") or {}
    suppressed = int(metrics.get("suppressed_signal_count", 0))
    detected = int(metrics.get("recursion_events_detected", 0))
    if detected > 50:
        return CheckResult(
            "recursion_guard",
            ValidationStatus.WARNING,
            f"high recursion events: {detected}",
            {"metrics": metrics},
        )
    return CheckResult(
        "recursion_guard",
        ValidationStatus.PASS,
        f"suppressed={suppressed} detected={detected}",
        {"current_depth": data.get("current_depth")},
    )


def _check_runtime_metrics(health: dict[str, Any] | None) -> CheckResult:
    if not health:
        return CheckResult("runtime_metrics", ValidationStatus.FAIL, "no health payload")
    loop_health = health.get("runtime_loop_health", "unknown")
    if loop_health == "critical":
        return CheckResult("runtime_metrics", ValidationStatus.FAIL, "runtime loop critical")
    if loop_health == "degraded":
        return CheckResult("runtime_metrics", ValidationStatus.WARNING, "runtime loop degraded")
    rate = float(health.get("kernel_processing_rate", 0))
    return CheckResult(
        "runtime_metrics",
        ValidationStatus.PASS,
        f"loop_health={loop_health} kernel_rate={rate}",
    )


def _check_perception_health(live: dict[str, Any] | None) -> CheckResult:
    if not live:
        return CheckResult("perception_health", ValidationStatus.FAIL, "no perception payload")
    count = int(live.get("count", 0))
    return CheckResult(
        "perception_health",
        ValidationStatus.PASS,
        f"live perceptions={count}",
        {"sample": (live.get("perceptions") or [])[:2]},
    )


def _check_active_cognition(kernel: dict[str, Any] | None) -> CheckResult:
    if not kernel:
        return CheckResult("active_cognition", ValidationStatus.FAIL, "no kernel state")
    signals = int(kernel.get("signal_count", 0))
    focus = kernel.get("current_focus", "")
    active = kernel.get("active_signals") or []
    if signals == 0 and not active:
        return CheckResult("active_cognition", ValidationStatus.WARNING, "no signals processed yet")
    return CheckResult(
        "active_cognition",
        ValidationStatus.PASS,
        f"signals={signals} focus={str(focus)[:60]}",
    )


def run_phase(
    base_url: str,
    *,
    timeout: float = 30.0,
    retries: int = 3,
) -> PhaseResult:
    client = ValidatorClient(base_url, timeout=timeout, retries=retries)
    phase = PhaseResult(phase="Runtime Stability")
    t0 = time.monotonic()

    if not client.health_ping():
        phase.add(CheckResult("api_reachable", ValidationStatus.FAIL, f"cannot reach {base_url}/api/v1/health"))
        phase.duration_seconds = time.monotonic() - t0
        return phase
    phase.add(CheckResult("api_reachable", ValidationStatus.PASS, base_url))

    payloads: dict[str, dict[str, Any] | None] = {}
    for path, name, keys in ENDPOINTS:
        check = _check_endpoint(client, path, name, keys)
        phase.add(check)
        if check.status != ValidationStatus.FAIL:
            _, data, _ = client.get_json(path)
            if isinstance(data, dict):
                payloads[name] = data

    phase.add(_check_recursion(client))
    phase.add(_check_runtime_metrics(payloads.get("runtime_health")))
    phase.add(_check_perception_health(payloads.get("perception_live")))
    phase.add(_check_active_cognition(payloads.get("kernel_state")))

    phase.duration_seconds = time.monotonic() - t0
    phase.metadata = {"endpoints_tested": len(ENDPOINTS)}
    return phase


def main() -> int:
    parser = argparse.ArgumentParser(description="ODIN Phase 1 — Runtime Stability")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="ODIN API base URL")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(level=args.log_level)
    phase = run_phase(args.base_url, timeout=args.timeout, retries=args.retries)
    console = ColoredConsole()

    if args.json:
        print(json.dumps(phase.to_dict(), indent=2))
    else:
        console.print_phase(phase)
        console.status_line(phase.status, f"Phase 1 result: {phase.status.value}")

    return 0 if phase.status == ValidationStatus.PASS else (1 if phase.status == ValidationStatus.FAIL else 2)


if __name__ == "__main__":
    raise SystemExit(main())

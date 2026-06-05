#!/usr/bin/env python3
"""Phase 3 — ODIN mission runtime validation."""

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

DEFAULT_OBJECTIVE = (
    "Inspect runtime health, verify memory systems, and summarize findings"
)
TERMINAL_STATES = frozenset({"completed", "failed", "cancelled"})


def run_phase(
    base_url: str,
    *,
    objective: str = DEFAULT_OBJECTIVE,
    start_worker: bool = True,
    poll_interval: float = 2.0,
    poll_timeout: float = 90.0,
    timeout: float = 30.0,
    retries: int = 3,
) -> PhaseResult:
    client = ValidatorClient(base_url, timeout=timeout, retries=retries)
    phase = PhaseResult(phase="Mission Runtime")
    t0 = time.monotonic()

    if not client.health_ping():
        phase.add(CheckResult("api_reachable", ValidationStatus.FAIL, "API not reachable"))
        phase.duration_seconds = time.monotonic() - t0
        return phase

    code, created, err = client.post_json(
        "/api/v1/missions/create",
        {
            "objective": objective,
            "start_worker": start_worker,
            "priority": 70,
            "autonomy_level": 1,
            "human_approved": False,
        },
        timeout=timeout,
    )

    if code != 200 or not isinstance(created, dict):
        phase.add(
            CheckResult(
                "mission_create",
                ValidationStatus.FAIL,
                err or f"HTTP {code}",
            )
        )
        phase.duration_seconds = time.monotonic() - t0
        return phase

    mission_id = created.get("mission_id")
    if not mission_id:
        phase.add(CheckResult("mission_create", ValidationStatus.FAIL, "no mission_id"))
        phase.duration_seconds = time.monotonic() - t0
        return phase

    phase.add(
        CheckResult(
            "mission_create",
            ValidationStatus.PASS,
            f"id={mission_id}",
            {"state": created.get("current_state")},
        )
    )
    phase.metadata["mission_id"] = mission_id

    deadline = time.monotonic() + poll_timeout
    last_state = created.get("current_state", "")
    waves_seen = 0

    while time.monotonic() < deadline:
        _, detail, _ = client.get_json(f"/api/v1/missions/{mission_id}")
        if isinstance(detail, dict):
            last_state = detail.get("current_state", last_state)
            history = detail.get("execution_history") or []
            waves_seen = max(waves_seen, len(history))
            checkpoints = detail.get("checkpoints") or []
            if last_state in TERMINAL_STATES:
                break
            if last_state in ("active", "waiting") and waves_seen >= 1 and len(checkpoints) >= 1:
                break
        time.sleep(poll_interval)

    _, detail, _ = client.get_json(f"/api/v1/missions/{mission_id}")
    if isinstance(detail, dict):
        phase.add(
            CheckResult(
                "mission_progression",
                ValidationStatus.PASS if waves_seen > 0 or last_state != "created" else ValidationStatus.WARNING,
                f"state={last_state} history_events={waves_seen}",
            )
        )
        ckpts = detail.get("checkpoints") or []
        phase.add(
            CheckResult(
                "mission_checkpoints",
                ValidationStatus.PASS if ckpts else ValidationStatus.WARNING,
                f"checkpoints={len(ckpts)}",
            )
        )
        phase.add(
            CheckResult(
                "adaptive_state",
                ValidationStatus.PASS if detail.get("adaptation_log") or detail.get("confidence") else ValidationStatus.WARNING,
                f"strategy={detail.get('execution_strategy')} confidence_keys={list((detail.get('confidence') or {}).keys())}",
            )
        )
        active = detail.get("active_tasks") or []
        completed = detail.get("completed_tasks") or []
        if last_state == "completed" or len(completed) >= 2:
            phase.add(CheckResult("mission_completion", ValidationStatus.PASS, last_state))
        elif last_state in TERMINAL_STATES:
            phase.add(CheckResult("mission_completion", ValidationStatus.WARNING, last_state))
        else:
            phase.add(
                CheckResult(
                    "mission_completion",
                    ValidationStatus.WARNING,
                    f"still {last_state} after poll",
                )
            )
    else:
        phase.add(CheckResult("mission_progression", ValidationStatus.FAIL, "cannot fetch mission"))

    _, timeline, _ = client.get_json(f"/api/v1/missions/{mission_id}/timeline")
    phase.add(
        CheckResult(
            "mission_timeline",
            ValidationStatus.PASS if isinstance(timeline, dict) and timeline.get("execution_history") is not None else ValidationStatus.FAIL,
            "timeline ok" if timeline else "missing",
        )
    )

    _, reasoning, _ = client.get_json(f"/api/v1/missions/{mission_id}/reasoning")
    phase.add(
        CheckResult(
            "mission_reasoning",
            ValidationStatus.PASS if isinstance(reasoning, dict) and "reasoning_log" in reasoning else ValidationStatus.WARNING,
            "reasoning endpoint ok",
        )
    )

    _, adapt, _ = client.get_json(f"/api/v1/missions/{mission_id}/adaptation-log")
    phase.add(
        CheckResult(
            "adaptation_log",
            ValidationStatus.PASS if isinstance(adapt, dict) else ValidationStatus.WARNING,
            f"log_entries={len((adapt or {}).get('adaptation_log', []))}" if isinstance(adapt, dict) else "n/a",
        )
    )

    _, listing, _ = client.get_json("/api/v1/missions", timeout=10.0)
    found = False
    if isinstance(listing, list):
        found = any(m.get("mission_id") == mission_id for m in listing)
    phase.add(
        CheckResult(
            "mission_persistence",
            ValidationStatus.PASS if found else ValidationStatus.WARNING,
            "listed in /missions" if found else "mission not in list (may be paginated)",
        )
    )

    phase.duration_seconds = time.monotonic() - t0
    return phase


def main() -> int:
    parser = argparse.ArgumentParser(description="ODIN Phase 3 — Mission Runtime")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--objective", default=DEFAULT_OBJECTIVE)
    parser.add_argument("--no-worker", action="store_true", help="Do not start mission worker")
    parser.add_argument("--poll-timeout", type=float, default=90.0)
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(level=args.log_level)
    phase = run_phase(
        args.base_url,
        objective=args.objective,
        start_worker=not args.no_worker,
        poll_timeout=args.poll_timeout,
        poll_interval=args.poll_interval,
        timeout=args.timeout,
    )
    console = ColoredConsole()

    if args.json:
        print(json.dumps(phase.to_dict(), indent=2))
    else:
        console.print_phase(phase)
        console.status_line(phase.status, f"Phase 3 result: {phase.status.value}")

    return 0 if phase.status == ValidationStatus.PASS else (1 if phase.status == ValidationStatus.FAIL else 2)


if __name__ == "__main__":
    raise SystemExit(main())

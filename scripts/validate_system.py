#!/usr/bin/env python3
"""Phase 5 — Unified ODIN system validation (all phases + local models)."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validator_lib.client import ValidatorClient
from validator_lib.console import ColoredConsole
from validator_lib.logging_config import setup_logging
from validator_lib.results import CheckResult, PhaseResult, ValidationStatus

import validate_runtime
import validate_cognition
import validate_missions

EXPECTED_MODELS = [
    ("deepseek-r1", ["deepseek-r1", "deepseek-r1:", "deepseek/r1"]),
    ("deepseek-coder", ["deepseek-coder", "deepseek-coder:", "deepseek-coder-v2"]),
    ("qwen2.5", ["qwen2.5", "qwen2:", "qwen"]),
    ("llama3", ["llama3", "llama3.2", "llama3:", "llama"]),
]


def _match_model(name: str, patterns: list[str]) -> bool:
    lower = name.lower()
    return any(p in lower for p in patterns)


def run_ollama_phase(
    ollama_url: str,
    *,
    timeout: float = 15.0,
    retries: int = 2,
) -> PhaseResult:
    client = ValidatorClient(ollama_url, timeout=timeout, retries=retries)
    phase = PhaseResult(phase="Local Model Runtime")
    t0 = time.monotonic()

    tags_url = f"{ollama_url.rstrip('/')}/api/tags"
    code, data, err = client.get_raw(tags_url, timeout=timeout)

    if err or code != 200 or not isinstance(data, dict):
        phase.add(
            CheckResult(
                "ollama_connectivity",
                ValidationStatus.FAIL,
                err or f"HTTP {code}",
            )
        )
        phase.duration_seconds = time.monotonic() - t0
        return phase

    phase.add(CheckResult("ollama_connectivity", ValidationStatus.PASS, ollama_url))

    models_raw = data.get("models") or []
    names = [m.get("name", "") for m in models_raw if isinstance(m, dict)]
    inventory = [{"name": n, "size": m.get("size")} for n, m in zip(names, models_raw) if isinstance(m, dict)]

    phase.metadata["model_inventory"] = inventory
    phase.metadata["model_count"] = len(names)

    if not names:
        phase.add(
            CheckResult(
                "local_model_availability",
                ValidationStatus.WARNING,
                "Ollama reachable but no models pulled",
            )
        )
    else:
        phase.add(
            CheckResult(
                "local_model_availability",
                ValidationStatus.PASS,
                f"{len(names)} model(s) installed",
                {"models": names[:20]},
            )
        )

    readiness: dict[str, str] = {}
    for label, patterns in EXPECTED_MODELS:
        matched = next((n for n in names if _match_model(n, patterns)), None)
        if matched:
            readiness[label] = f"available ({matched})"
            phase.add(
                CheckResult(
                    f"model_{label}",
                    ValidationStatus.PASS,
                    matched,
                )
            )
        else:
            readiness[label] = "not_found"
            phase.add(
                CheckResult(
                    f"model_{label}",
                    ValidationStatus.WARNING,
                    "not in Ollama tags (optional pull)",
                )
            )

    available_count = sum(1 for v in readiness.values() if v.startswith("available"))
    if available_count == 0 and names:
        summary_status = ValidationStatus.WARNING
        summary_msg = "models present but none match expected aliases"
    elif available_count >= 2:
        summary_status = ValidationStatus.PASS
        summary_msg = f"{available_count}/{len(EXPECTED_MODELS)} expected families found"
    else:
        summary_status = ValidationStatus.WARNING
        summary_msg = f"{available_count}/{len(EXPECTED_MODELS)} expected families found"

    phase.add(
        CheckResult(
            "inference_readiness",
            summary_status,
            summary_msg,
            {"readiness": readiness},
        )
    )

    phase.metadata["inference_readiness"] = readiness
    phase.duration_seconds = time.monotonic() - t0
    return phase


def aggregate_status(phases: list[PhaseResult]) -> ValidationStatus:
    if any(p.status == ValidationStatus.FAIL for p in phases):
        return ValidationStatus.FAIL
    if any(p.status == ValidationStatus.WARNING for p in phases):
        return ValidationStatus.WARNING
    return ValidationStatus.PASS


def build_system_report(
    phases: list[PhaseResult],
    *,
    base_url: str,
    ollama_url: str,
    skip_cognition: bool,
    skip_missions: bool,
) -> dict[str, Any]:
    overall = aggregate_status(phases)
    warnings: list[str] = []
    errors: list[str] = []

    for phase in phases:
        for check in phase.checks:
            if check.status == ValidationStatus.WARNING:
                warnings.append(f"[{phase.phase}] {check.name}: {check.message}")
            elif check.status == ValidationStatus.FAIL:
                errors.append(f"[{phase.phase}] {check.name}: {check.message}")

    runtime_phase = next((p for p in phases if "Runtime" in p.phase), None)
    cognition_phase = next((p for p in phases if "Cognitive" in p.phase), None)
    mission_phase = next((p for p in phases if "Mission" in p.phase), None)
    ollama_phase = next((p for p in phases if "Local" in p.phase), None)

    stability = "unknown"
    if runtime_phase:
        for c in runtime_phase.checks:
            if c.name == "runtime_metrics":
                stability = c.message
                break

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall.value,
        "api_base": base_url,
        "ollama_base": ollama_url,
        "runtime_status": runtime_phase.status.value if runtime_phase else "skipped",
        "cognition_readiness": "skipped" if skip_cognition else (cognition_phase.status.value if cognition_phase else "unknown"),
        "mission_readiness": "skipped" if skip_missions else (mission_phase.status.value if mission_phase else "unknown"),
        "local_model_readiness": ollama_phase.status.value if ollama_phase else "skipped",
        "stability_assessment": stability,
        "warnings": warnings,
        "errors": errors,
        "phases": [p.to_dict() for p in phases],
    }


def run_all(
    base_url: str,
    ollama_url: str,
    *,
    skip_cognition: bool = False,
    skip_missions: bool = False,
    skip_ollama: bool = False,
    cognition_timeout: float = 120.0,
    mission_poll_timeout: float = 90.0,
    quick: bool = False,
) -> tuple[list[PhaseResult], dict[str, Any]]:
    phases: list[PhaseResult] = []

    phases.append(
        validate_runtime.run_phase(base_url, timeout=20.0 if quick else 30.0)
    )

    if not skip_ollama:
        phases.append(run_ollama_phase(ollama_url, timeout=10.0 if quick else 15.0))

    if not skip_cognition:
        phases.append(
            validate_cognition.run_phase(
                base_url,
                timeout=cognition_timeout if not quick else 60.0,
                retries=1 if quick else 2,
            )
        )

    if not skip_missions:
        phases.append(
            validate_missions.run_phase(
                base_url,
                start_worker=True,
                poll_timeout=30.0 if quick else mission_poll_timeout,
                poll_interval=1.5 if quick else 2.0,
            )
        )

    report = build_system_report(
        phases,
        base_url=base_url,
        ollama_url=ollama_url,
        skip_cognition=skip_cognition,
        skip_missions=skip_missions,
    )
    return phases, report


def watch_loop(
    base_url: str,
    ollama_url: str,
    interval: float,
    **kwargs: Any,
) -> None:
    console = ColoredConsole()
    console.header(f"ODIN Watch Mode — every {interval}s (Ctrl+C to stop)")
    try:
        while True:
            phases, report = run_all(base_url, ollama_url, **kwargs)
            console.header(f"Tick {report['timestamp']} — {report['overall_status']}")
            for phase in phases:
                console.status_line(phase.status, phase.phase)
            if report["errors"]:
                for e in report["errors"][:5]:
                    console.fail(e)
            time.sleep(interval)
    except KeyboardInterrupt:
        console.info("watch stopped")


def main() -> int:
    parser = argparse.ArgumentParser(description="ODIN Unified System Validation")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--skip-cognition", action="store_true")
    parser.add_argument("--skip-missions", action="store_true")
    parser.add_argument("--skip-ollama", action="store_true")
    parser.add_argument("--quick", action="store_true", help="Shorter timeouts and mission poll")
    parser.add_argument("--watch", type=float, metavar="SECONDS", help="Continuous monitoring interval")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=str, help="Write JSON report to file")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(level=args.log_level)
    console = ColoredConsole()

    kwargs = {
        "skip_cognition": args.skip_cognition,
        "skip_missions": args.skip_missions,
        "skip_ollama": args.skip_ollama,
        "quick": args.quick,
    }

    if args.watch:
        watch_loop(args.base_url, args.ollama_url, args.watch, **kwargs)
        return 0

    console.header("ODIN Unified Runtime Validation")
    phases, report = run_all(args.base_url, args.ollama_url, **kwargs)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for phase in phases:
            console.print_phase(phase)
        console.header(f"SYSTEM REPORT — {report['overall_status']}")
        console.info(f"Runtime:        {report['runtime_status']}")
        console.info(f"Cognition:      {report['cognition_readiness']}")
        console.info(f"Missions:       {report['mission_readiness']}")
        console.info(f"Local models:   {report['local_model_readiness']}")
        console.info(f"Stability:      {report['stability_assessment']}")
        for w in report["warnings"][:10]:
            console.warn(w)
        for e in report["errors"][:10]:
            console.fail(e)
        console.status_line(
            ValidationStatus(report["overall_status"]),
            f"Overall: {report['overall_status']}",
        )

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
        console.info(f"report written to {args.output}")

    overall = ValidationStatus(report["overall_status"])
    return 0 if overall == ValidationStatus.PASS else (1 if overall == ValidationStatus.FAIL else 2)


if __name__ == "__main__":
    raise SystemExit(main())

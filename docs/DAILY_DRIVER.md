# Daily Driver Guide

Odin v0.37 is hardened for **all-day, every-day** use on a personal machine with low supervision.

## What changed

- One-command install and bootstrap
- Daemon modes: desktop assistant, overnight cognition, passive observer, low-power
- Performance and memory pressure management
- Daily workflow suggestions on startup
- Operator command center for natural-language control
- Privacy filters and local credential vault
- Recovery reports and safe-boot mode

## Recommended settings

```env
ODIN_DEPLOYMENT_ENABLED=1
ODIN_PERFORMANCE_ENABLED=1
ODIN_PRIVACY_ENABLED=1
ODIN_OPERATOR_SHELL_ENABLED=1
ODIN_DAILY_DRIVER_ENABLED=1
ODIN_DAEMON_MODE_ENABLED=1
ODIN_RUNTIME_GUARDIAN_ENABLED=1
```

## Operator pages

- `/runtime/deployment` — profile and platform
- `/runtime/activity` — startup suggestions
- `/runtime/command-center` — natural commands
- `/runtime/diagnostics` — health panel
- `/runtime/recovery-report` — overnight recovery summary

## Daily flow

1. Start Odin (daemon or foreground)
2. Review activity center suggestions
3. Resume project or session from command center
4. Let idle consolidation run during breaks

No cloud telemetry. Local-first only.

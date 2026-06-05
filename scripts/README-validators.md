# ODIN Runtime Validation Suite

Diagnostics-only scripts. They do not modify ODIN architecture.

## Prerequisites

- ODIN API running (`uvicorn` on port 8000)
- Python 3.11+ with `httpx` (use backend venv)

```powershell
cd odin\backend
.\.venv\Scripts\pip install httpx

cd ..\scripts
```

## Scripts

| Script | Phase | Description |
|--------|-------|-------------|
| `validate_runtime.py` | 1 | Runtime health, signals, confidence, perception, kernel |
| `validate_cognition.py` | 2 | Live cognitive cycle |
| `validate_missions.py` | 3 | Mission create, poll, timeline, adaptation |
| `validate_system.py` | 4+5 | Ollama models + unified PASS/WARN/FAIL report |

## Quick start

```powershell
# Full system validation
python validate_system.py --base-url http://127.0.0.1:8000

# JSON report
python validate_system.py --json --output report.json

# Continuous watch (every 60s)
python validate_system.py --watch 60

# Fast check (skip slow phases)
python validate_system.py --quick --skip-cognition

# Individual phases
python validate_runtime.py
python validate_cognition.py --timeout 180
python validate_missions.py --poll-timeout 120
```

## Environment

| Variable | Default |
|----------|---------|
| `--base-url` | `http://127.0.0.1:8000` |
| `--ollama-url` | `http://localhost:11434` |

## Exit codes

- `0` — PASS
- `1` — FAIL
- `2` — WARNING

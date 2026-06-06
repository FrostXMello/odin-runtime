#!/usr/bin/env bash
# Odin Runtime — startup script (Linux/macOS)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT/backend"
source .venv/bin/activate
export ODIN_DEPLOYMENT_ENABLED=1
export ODIN_PERFORMANCE_ENABLED=1
export ODIN_DAILY_DRIVER_ENABLED=1
exec uvicorn odin_backend.api.main:create_api --factory --host 127.0.0.1 --port 8000

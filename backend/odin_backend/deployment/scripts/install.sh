#!/usr/bin/env bash
# Odin Runtime — Linux/macOS bootstrap installer
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT/backend"
python -m venv .venv
source .venv/bin/activate
pip install -U pip wheel
pip install -e ".[dev]"
python -c "from odin_backend.deployment.environment_validator import validate_environment; print(validate_environment())"
python -c "from odin_backend.deployment.dependency_manager import check_dependencies; print(check_dependencies())"
echo "Odin bootstrap complete. Run: cd backend && source .venv/bin/activate && uvicorn odin_backend.api.main:create_api --factory --host 0.0.0.0 --port 8000"

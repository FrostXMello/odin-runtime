# Odin Runtime — Windows bootstrap installer
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location (Join-Path $Root "backend")
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install -U pip wheel
pip install -e ".[dev]"
python -c "from odin_backend.deployment.environment_validator import validate_environment; print(validate_environment())"
python -c "from odin_backend.deployment.dependency_manager import check_dependencies; print(check_dependencies())"
Write-Host "Odin bootstrap complete. Run backend with .venv activated."

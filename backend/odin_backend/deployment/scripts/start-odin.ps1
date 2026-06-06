# Odin Runtime — startup script (Windows)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location (Join-Path $Root "backend")
& .\.venv\Scripts\Activate.ps1
$env:ODIN_DEPLOYMENT_ENABLED = "1"
$env:ODIN_PERFORMANCE_ENABLED = "1"
$env:ODIN_DAILY_DRIVER_ENABLED = "1"
uvicorn odin_backend.api.main:create_api --factory --host 127.0.0.1 --port 8000

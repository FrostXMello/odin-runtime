# Start ODIN backend
$BackendRoot = Join-Path $PSScriptRoot "..\backend"
Set-Location $BackendRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
$env:PYTHONPATH = $BackendRoot
python main.py

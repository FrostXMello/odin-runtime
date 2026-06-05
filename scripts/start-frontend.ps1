# Start ODIN Electron + React dev
$FrontendRoot = Join-Path $PSScriptRoot "..\frontend"
Set-Location $FrontendRoot

if (-not (Test-Path "node_modules")) {
    npm install
}

npm run electron:dev

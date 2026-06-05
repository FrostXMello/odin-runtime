# Start Redis via Docker Compose
$DockerDir = Join-Path $PSScriptRoot "..\infrastructure\docker"
Set-Location $DockerDir
docker compose up -d redis
Write-Host "Redis started on localhost:6379"

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $repoRoot

if (-not (Test-Path -LiteralPath '.env')) {
    throw 'Create a root .env from .env.example and set MSSQL_SA_PASSWORD.'
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker CLI is unavailable. Install Docker Desktop and start its engine.'
}

docker compose up -d --build
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose startup failed. Check docker compose logs.' }
docker compose ps

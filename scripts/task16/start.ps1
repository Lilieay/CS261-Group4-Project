$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $repoRoot

if (-not (Test-Path -LiteralPath '.env')) {
    throw 'Create a root .env from .env.example and set MSSQL_SA_PASSWORD.'
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker CLI is unavailable. Install Docker Desktop and start its engine.'
}

$previousErrorAction = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
docker info *> $null
$dockerInfoExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorAction
if ($dockerInfoExitCode -ne 0) {
    throw 'Docker engine is unavailable. Start Docker Desktop and retry.'
}

$envContent = Get-Content -LiteralPath '.env' -Raw
if ($envContent -notmatch '(?m)^\s*MSSQL_SA_PASSWORD\s*=\s*\S+') {
    throw 'MSSQL_SA_PASSWORD is missing from root .env.'
}

docker compose build backend
if ($LASTEXITCODE -ne 0) { throw 'Backend image build failed.' }

docker compose up -d sqlserver
if ($LASTEXITCODE -ne 0) { throw 'SQL Server startup failed.' }

$ready = $false
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    $containerId = docker compose ps -q sqlserver
    if ($LASTEXITCODE -eq 0 -and $containerId) {
        $health = docker inspect --format '{{.State.Health.Status}}' $containerId
        if ($LASTEXITCODE -eq 0 -and $health -eq 'healthy') {
            $ready = $true
            break
        }
    }
    Start-Sleep -Seconds 5
}
if (-not $ready) { throw 'SQL Server did not become healthy within five minutes.' }

docker compose exec -T sqlserver sh -c 'SQLCMDPASSWORD="$MSSQL_SA_PASSWORD" /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C -b -i /docker-entrypoint-initdb.d/init.sql'
if ($LASTEXITCODE -ne 0) { throw 'Database bootstrap failed.' }

docker compose run --rm --no-deps backend python -m app.init_db
if ($LASTEXITCODE -ne 0) { throw 'ORM table creation failed.' }

docker compose up -d backend
if ($LASTEXITCODE -ne 0) { throw 'Backend startup failed.' }

$backendReady = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/' -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    } catch { }
    Start-Sleep -Seconds 2
}
if (-not $backendReady) { throw 'Backend did not become ready.' }

Write-Output 'Backend: http://127.0.0.1:8000'
Write-Output 'Login API: http://127.0.0.1:8000/api/auth/login'

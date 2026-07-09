[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$root = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $root 'docker-compose.yml'
$sqlFile = Join-Path $PSScriptRoot 'verification.sql'
$sql = Get-Content -Raw -LiteralPath $sqlFile

docker compose -f $composeFile up -d | Out-Host
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose failed to start the local test databases.' }

$deadline = (Get-Date).AddMinutes(3)
do {
    $state = docker compose -f $composeFile ps --format json | ConvertFrom-Json
    $healthy = @($state | Where-Object { $_.Health -eq 'healthy' }).Count -eq 2
    if (-not $healthy) { Start-Sleep -Seconds 3 }
} until ($healthy -or (Get-Date) -gt $deadline)
if (-not $healthy) { throw 'MySQL and PostgreSQL did not become healthy within three minutes.' }

Write-Host "`n=== MySQL acceptance SQL ==="
$sql | docker exec -i dify-plugin-test-mysql mysql -h 127.0.0.1 -uplugin_test_user -pplugin_test_password plugin_test
if ($LASTEXITCODE -ne 0) { throw 'MySQL acceptance SQL failed.' }

Write-Host "`n=== PostgreSQL acceptance SQL ==="
$env:PGPASSWORD = 'plugin_test_password'
try {
    $sql | docker exec -e PGPASSWORD=$env:PGPASSWORD -i dify-plugin-test-postgres psql -U plugin_test_user -d plugin_test
    if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL acceptance SQL failed.' }
} finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
}

Write-Host "`nAcceptance complete: both databases returned the LIMIT, COUNT, WHERE, JOIN, aggregation, and time-query result sets."

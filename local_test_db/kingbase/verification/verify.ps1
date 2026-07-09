[CmdletBinding()]
param(
    [string]$ContainerName = "dify-plugin-test-kingbase",
    [string]$KsqlPath = $env:KINGBASE_KSQL_PATH
)

$ErrorActionPreference = "Stop"

if (-not $env:KINGBASE_IMAGE) {
    throw "BLOCKED: KINGBASE_IMAGE is not set. Load and select the vendor-provided image first."
}
if (-not $env:KINGBASE_ADMIN_PASSWORD) {
    throw "BLOCKED: KINGBASE_ADMIN_PASSWORD must be supplied through the current process environment."
}
if (-not $KsqlPath) {
    throw "BLOCKED: KINGBASE_KSQL_PATH must be set to the actual ksql path inside the supplied image."
}

$container = docker inspect $ContainerName 2>$null | ConvertFrom-Json
if (-not $container -or $container[0].State.Status -ne "running") {
    throw "BLOCKED: KingbaseES container '$ContainerName' is not running."
}

$scriptPath = "/opt/phase10-verification/verify.sql"
docker exec `
    -e PGPASSWORD=plugin_readonly_123 `
    $ContainerName `
    $KsqlPath `
    -h 127.0.0.1 `
    -p 54321 `
    -U plugin_readonly `
    -d plugin_test `
    -v ON_ERROR_STOP=1 `
    -f $scriptPath

if ($LASTEXITCODE -ne 0) {
    throw "KingbaseES verification failed."
}

Write-Host "[kingbase] PASS - version, encoding, search_path, SELECT 1, LIMIT, COUNT, Unicode, timestamp, and privileges queried."

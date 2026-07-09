[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$required = @("KINGBASE_IMAGE", "KINGBASE_ADMIN_PASSWORD")
$missing = @($required | Where-Object { -not (Get-Item "Env:$_" -ErrorAction SilentlyContinue).Value })
if ($missing.Count -gt 0) {
    Write-Host "[kingbase] BLOCKED"
    Write-Host "Missing environment variables: $($missing -join ', ')"
    Write-Host "Obtain and load a licensed vendor image; do not substitute an unverified public image."
    exit 2
}

$image = docker image inspect $env:KINGBASE_IMAGE 2>$null | ConvertFrom-Json
if (-not $image) {
    Write-Host "[kingbase] BLOCKED - image is not loaded locally: $env:KINGBASE_IMAGE"
    exit 2
}

docker compose config
if ($LASTEXITCODE -ne 0) {
    throw "KingbaseES Compose configuration is invalid for the supplied image variables."
}

Write-Host "[kingbase] PREPARED - image exists and Compose renders. Review vendor startup/license requirements before docker compose up."

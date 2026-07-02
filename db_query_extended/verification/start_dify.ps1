[CmdletBinding()]
param(
    [switch]$SkipPreflight
)

$ErrorActionPreference = "Stop"

$ComposeDirectory = "/home/zli2759/projects/dify-dm/docker"
$ComposeFile = "$ComposeDirectory/docker-compose.yaml"
$PluginOverride = "/home/zli2759/projects/dify-dm/outputs/dm_change_matrix/regression_scripts/plugin_daemon.local.override.yaml"
$MiddlewareOverride = "/mnt/e/Dify_Plugin/db_query_extended/verification/dify.middleware.override.yaml"
$BaselineOverride = "/mnt/e/Dify_Plugin/db_query_extended/verification/dify.baseline.override.yaml"

$dockerDeadline = (Get-Date).AddMinutes(2)
do {
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & wsl -e bash -lc "docker info >/dev/null 2>&1" 2>$null
    $dockerReady = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $previousErrorAction
    if ($dockerReady) { break }
    if ((Get-Date) -ge $dockerDeadline) {
        throw "Docker Desktop WSL integration did not become ready within 2 minutes."
    }
    Start-Sleep -Seconds 3
} while ($true)

$previousErrorAction = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$duplicateContainers = & wsl -e bash -lc "docker ps --filter label=com.docker.compose.project=docker --format '{{.Names}}'" 2>&1
$duplicateCheckExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorAction
if ($duplicateCheckExitCode -ne 0) {
    throw ($duplicateContainers -join [Environment]::NewLine)
}
if (@($duplicateContainers).Count -gt 0 -and @($duplicateContainers)[0]) {
    throw "Duplicate Compose project 'docker' is running. Stop that project before using this launcher."
}

Write-Host "[start_dify] Starting the fixed Compose project 'dify'..."
$previousErrorAction = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& wsl -e bash -lc "docker compose -p dify --profile postgresql --profile weaviate -f '$ComposeFile' -f '$PluginOverride' -f '$MiddlewareOverride' -f '$BaselineOverride' up -d" 2>&1
$composeExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorAction
if ($composeExitCode -ne 0) {
    throw "Dify Compose startup failed."
}

if (-not $SkipPreflight) {
    & "$PSScriptRoot\dify_preflight.ps1"
}

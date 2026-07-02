[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$SkipStart
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$StartScript = Join-Path $Root 'db_query_extended\verification\start_dify.ps1'
$PreflightScript = Join-Path $Root 'db_query_extended\verification\dify_preflight.ps1'
$ExpectedRoot = 'E:\Dify_Plugin'
$DifyWslRoot = '/home/zli2759/projects/dify-dm'

function Assert-Command {
    param([Parameter(Mandatory)][string]$Name, [Parameter(Mandatory)][string]$Help)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing command '$Name'. $Help"
    }
    Write-Host "[bootstrap] ${Name}: PASS"
}

function Invoke-WslCheck {
    param([Parameter(Mandatory)][string]$Command, [Parameter(Mandatory)][string]$Failure)
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & wsl -e bash -lc $Command 2>$null | Out-Null
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previous
    if ($exitCode -ne 0) { throw $Failure }
}

Write-Host '[bootstrap] Checking v1.0 baseline prerequisites...'
Assert-Command -Name 'git' -Help 'Install Git for Windows.'
Assert-Command -Name 'wsl' -Help 'Enable WSL 2 and install a Linux distribution.'
Assert-Command -Name 'python' -Help 'Install Python 3.11 for development tooling.'

if ([IO.Path]::GetFullPath($Root).TrimEnd('\') -ne $ExpectedRoot) {
    throw "This frozen launcher currently expects '$ExpectedRoot'. Clone there, or explicitly migrate the baseline paths before use. Current path: '$Root'."
}

foreach ($path in @($StartScript, $PreflightScript)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Required baseline file is missing: $path" }
}

Invoke-WslCheck -Command 'docker info >/dev/null 2>&1' -Failure 'Docker Desktop or its WSL integration is not ready.'
Write-Host '[bootstrap] Docker through WSL: PASS'
Invoke-WslCheck -Command "test -f '$DifyWslRoot/docker/docker-compose.yaml'" -Failure "The frozen Dify source tree is missing at $DifyWslRoot. Restore the accepted fork before startup."
Write-Host '[bootstrap] Fixed Dify source tree: PASS'

if ($CheckOnly) {
    Write-Host '[bootstrap] Prerequisite check completed. No services were changed.'
    exit 0
}

if (-not $SkipStart) {
    Write-Host '[bootstrap] Starting only through the frozen entry point...'
    & $StartScript
} else {
    Write-Host '[bootstrap] Startup skipped; running preflight against the existing stack...'
    & $PreflightScript
}

Write-Host '[bootstrap] Baseline runtime is ready. Provider credentials and Workflow API keys remain manual secrets.'

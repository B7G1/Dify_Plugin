[CmdletBinding()]
param(
    [string]$ContainerName = "dify-plugin-test-sqlserver",
    [string]$LogPath
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $LogPath) {
    $LogPath = Join-Path $Root "logs\verify-$((Get-Date).ToString('yyyyMMdd-HHmmss')).log"
}
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LogPath) | Out-Null

function Write-Evidence([string]$Message) {
    $line = "[$((Get-Date).ToUniversalTime().ToString('o'))] $Message"
    $line | Tee-Object -FilePath $LogPath -Append
}

function Invoke-NativeCommand([scriptblock]$Command) {
    $previousErrorActionPreference = $ErrorActionPreference
    $nativePreferenceExists = Test-Path Variable:PSNativeCommandUseErrorActionPreference
    if ($nativePreferenceExists) {
        $previousNativePreference = $PSNativeCommandUseErrorActionPreference
    }
    try {
        $ErrorActionPreference = "Continue"
        if ($nativePreferenceExists) {
            $PSNativeCommandUseErrorActionPreference = $false
        }
        $nativeOutput = & $Command 2>&1
        $nativeExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
        if ($nativePreferenceExists) {
            $PSNativeCommandUseErrorActionPreference = $previousNativePreference
        }
    }
    [pscustomobject]@{ ExitCode = [int]$nativeExitCode; Output = [object[]]@($nativeOutput) }
}

function Write-NativeResult([string]$Name, $Result) {
    if ($Result.Output.Count -gt 0) {
        $Result.Output | Tee-Object -FilePath $LogPath -Append
    }
    Write-Evidence "$Name exit code=$($Result.ExitCode)."
}

if (-not $env:MSSQL_READONLY_PASSWORD) {
    Write-Evidence "BLOCKED: MSSQL_READONLY_PASSWORD is not set in the current process."
    exit 2
}

$native = Invoke-NativeCommand { docker inspect -f "{{.State.Running}}" $ContainerName }
$running = if ($native.Output.Count -gt 0) { "$($native.Output[-1])".Trim() } else { "" }
if ($native.ExitCode -ne 0 -or $running -ne "true") {
    Write-Evidence "BLOCKED: SQL Server container '$ContainerName' is not running."
    exit 2
}

$native = Invoke-NativeCommand { docker exec $ContainerName sh -lc "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then echo /opt/mssql-tools18/bin/sqlcmd; elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then echo /opt/mssql-tools/bin/sqlcmd; else exit 1; fi" }
Write-NativeResult "Locate sqlcmd" $native
$sqlcmd = if ($native.Output.Count -gt 0) { "$($native.Output[-1])".Trim() } else { "" }
if ($native.ExitCode -ne 0 -or -not $sqlcmd) {
    Write-Evidence "BLOCKED: sqlcmd was not found in the official image."
    exit 2
}
Write-Evidence "Running SQL Server verification as plugin_readonly."
$native = Invoke-NativeCommand {
    docker exec `
        -e "SQLCMDPASSWORD=$($env:MSSQL_READONLY_PASSWORD)" `
        $ContainerName `
        $sqlcmd -C -S localhost -U plugin_readonly -d plugin_test `
        -b -r 1 -i /opt/phase11-verification/verify.sql
}
Write-NativeResult "Readonly verification" $native
$output = $native.Output
$exitCode = $native.ExitCode

if ($exitCode -ne 0 -or -not ($output -match "PHASE11_SQLSERVER_VERIFY_PASS")) {
    Write-Evidence "FAIL: SQL Server verification returned exit code $exitCode."
    exit 1
}

Write-Evidence "PASS: SELECT, TOP 5, COUNT, Unicode, JOIN, aggregation, deterministic counts, and permissions passed."
exit 0

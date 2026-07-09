[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogPath = Join-Path $Root "logs\prepare-$((Get-Date).ToString('yyyyMMdd-HHmmss')).log"
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
        # Native tools commonly write informational messages to stderr. Capture
        # both streams and use only the process exit code as the success signal.
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

    [pscustomobject]@{
        ExitCode = [int]$nativeExitCode
        Output = [object[]]@($nativeOutput)
    }
}

function Write-NativeResult([string]$Name, $Result) {
    if ($Result.Output.Count -gt 0) {
        $Result.Output | Tee-Object -FilePath $LogPath -Append
    }
    Write-Evidence "$Name exit code=$($Result.ExitCode)."
}

Write-Evidence "Phase 11.1 SQL Server environment gate started."

if ($env:ACCEPT_EULA -ne "Y") {
    Write-Evidence "BLOCKED: Microsoft EULA has not been explicitly accepted in this process. Review the terms, then set ACCEPT_EULA=Y manually."
    exit 2
}
if (-not $env:MSSQL_SA_PASSWORD) {
    Write-Evidence "BLOCKED: MSSQL_SA_PASSWORD is not set in the current process."
    exit 2
}
if (-not $env:MSSQL_READONLY_PASSWORD) {
    Write-Evidence "BLOCKED: MSSQL_READONLY_PASSWORD is not set in the current process."
    exit 2
}

Set-Location $Root
Write-Evidence "EULA flag is explicit. Pulling Microsoft official SQL Server 2022 image."
$native = Invoke-NativeCommand { docker pull mcr.microsoft.com/mssql/server:2022-latest }
Write-NativeResult "Docker pull" $native
if ($native.ExitCode -ne 0) {
    Write-Evidence "BLOCKED: Docker pull failed."
    exit 2
}

$native = Invoke-NativeCommand { docker compose config --quiet }
Write-NativeResult "Docker Compose config" $native
if ($native.ExitCode -ne 0) {
    Write-Evidence "BLOCKED: Docker Compose configuration failed."
    exit 2
}

$native = Invoke-NativeCommand { docker compose up -d }
Write-NativeResult "Docker Compose up" $native
if ($native.ExitCode -ne 0) {
    Write-Evidence "BLOCKED: SQL Server container startup failed."
    exit 2
}

$deadline = (Get-Date).AddMinutes(6)
$health = ""
do {
    Start-Sleep -Seconds 5
    $native = Invoke-NativeCommand { docker inspect -f "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}" dify-plugin-test-sqlserver }
    $health = if ($native.ExitCode -eq 0 -and $native.Output.Count -gt 0) { "$($native.Output[-1])".Trim() } else { "inspect-error-$($native.ExitCode)" }
    Write-Evidence "Container health=$health"
} while ($health -ne "healthy" -and (Get-Date) -lt $deadline)

if ($health -ne "healthy") {
    $native = Invoke-NativeCommand { docker logs --tail 100 dify-plugin-test-sqlserver }
    Write-NativeResult "Docker logs" $native
    Write-Evidence "BLOCKED: SQL Server did not become healthy."
    exit 2
}

$native = Invoke-NativeCommand { docker exec dify-plugin-test-sqlserver sh -lc "if [ -x /opt/mssql-tools18/bin/sqlcmd ]; then echo /opt/mssql-tools18/bin/sqlcmd; elif [ -x /opt/mssql-tools/bin/sqlcmd ]; then echo /opt/mssql-tools/bin/sqlcmd; else exit 1; fi" }
Write-NativeResult "Locate sqlcmd" $native
$sqlcmd = if ($native.Output.Count -gt 0) { "$($native.Output[-1])".Trim() } else { "" }
if ($native.ExitCode -ne 0 -or -not $sqlcmd) {
    Write-Evidence "BLOCKED: sqlcmd was not found in the official image."
    exit 2
}
Write-Evidence "Initializing database, schema, login, and deterministic data."
$native = Invoke-NativeCommand {
    docker exec `
        -e "SQLCMDPASSWORD=$($env:MSSQL_SA_PASSWORD)" `
        dify-plugin-test-sqlserver `
        $sqlcmd -C -S localhost -U sa -d master -b -r 1 `
        -v "ReadonlyPassword=$($env:MSSQL_READONLY_PASSWORD)" `
        -i /opt/phase11-init/01_admin_setup.sql
}
Write-NativeResult "Administrator initialization" $native
if ($native.ExitCode -ne 0) {
    Write-Evidence "BLOCKED: administrator initialization failed."
    exit 2
}

$native = Invoke-NativeCommand {
    docker exec `
        -e "SQLCMDPASSWORD=$($env:MSSQL_SA_PASSWORD)" `
        dify-plugin-test-sqlserver `
        $sqlcmd -C -S localhost -U sa -d plugin_test -b -r 1 `
        -i /opt/phase11-init/02_schema_data.sql
}
Write-NativeResult "Deterministic fixture initialization" $native
if ($native.ExitCode -ne 0) {
    Write-Evidence "BLOCKED: deterministic data initialization failed."
    exit 2
}

& (Join-Path $Root "verification\verify.ps1") -LogPath (Join-Path $Root "logs\verification-latest.log")
$verifyExit = $LASTEXITCODE
if ($verifyExit -ne 0) {
    Write-Evidence "BLOCKED: SQL verification did not pass; verify exit=$verifyExit."
    exit 2
}

Write-Evidence "PASS: SQL Server environment gate completed with the official image."
exit 0

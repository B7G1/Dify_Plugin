[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ComposeProject = "dify"
$PostgresContainer = "dify-db_postgres-1"
$ExpectedPostgresVolume = "dify_postgres_data_v1"
$ExpectedWeaviateVolume = "dify_weaviate_data_v1"
$ExpectedAppStorageVolume = "dify_app_storage"
$RequiredDatabases = @("dify", "dify_plugin")

function Invoke-WslBash {
    param([Parameter(Mandatory)][string]$Command)

    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & wsl -e bash -lc $Command 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorAction
    if ($exitCode -ne 0) {
        throw ($output -join [Environment]::NewLine)
    }
    return @($output)
}

Write-Host "[preflight] Compose project: $ComposeProject"

$duplicateContainers = Invoke-WslBash "docker ps --filter label=com.docker.compose.project=docker --format '{{.Names}}'"
if ($duplicateContainers.Count -gt 0 -and $duplicateContainers[0]) {
    throw "Duplicate Compose project 'docker' is running: $($duplicateContainers -join ', '). Stop it before starting Dify."
}

$difyContainers = Invoke-WslBash "docker ps --filter label=com.docker.compose.project=$ComposeProject --format '{{.Names}}'"
if ($difyContainers.Count -eq 0 -or -not $difyContainers[0]) {
    throw "No running containers were found for Compose project '$ComposeProject'."
}

$containerInfo = (((Invoke-WslBash "docker inspect $PostgresContainer") -join [Environment]::NewLine) | ConvertFrom-Json)[0]
$postgresProject = $containerInfo.Config.Labels.'com.docker.compose.project'
if ($postgresProject -ne $ComposeProject) {
    throw "$PostgresContainer belongs to Compose project '$postgresProject', expected '$ComposeProject'."
}

$postgresData = $containerInfo.Mounts | Where-Object Destination -eq "/var/lib/postgresql/data"
if ($postgresData.Type -ne "volume" -or $postgresData.Name -ne $ExpectedPostgresVolume) {
    throw "PostgreSQL is not using fixed named volume '$ExpectedPostgresVolume'."
}
Write-Host "[preflight] PostgreSQL named volume: $ExpectedPostgresVolume"

$weaviateInfo = (((Invoke-WslBash "docker inspect dify-weaviate-1") -join [Environment]::NewLine) | ConvertFrom-Json)[0]
$weaviateData = $weaviateInfo.Mounts | Where-Object Destination -eq "/var/lib/weaviate"
if ($weaviateData.Type -ne "volume" -or $weaviateData.Name -ne $ExpectedWeaviateVolume) {
    throw "Weaviate is not using fixed named volume '$ExpectedWeaviateVolume'."
}
Write-Host "[preflight] Weaviate named volume: $ExpectedWeaviateVolume"

$databaseRows = Invoke-WslBash "docker exec $PostgresContainer psql -U postgres -lAt"
$databaseNames = @($databaseRows | ForEach-Object { ($_ -split '\|', 2)[0] })
foreach ($database in $RequiredDatabases) {
    if ($database -notin $databaseNames) {
        throw "Required PostgreSQL database '$database' does not exist."
    }
    Write-Host "[preflight] Database '$database': PASS"
}

$accountCount = (Invoke-WslBash "docker exec $PostgresContainer psql -U postgres -d dify -At -c 'SELECT count(*) FROM accounts'")[0]
$parsedAccountCount = 0
if (-not [int]::TryParse($accountCount, [ref]$parsedAccountCount) -or $parsedAccountCount -lt 1) {
    throw "Dify database exists, but accounts contains no administrator record. Opening /install will request setup again."
}
Write-Host "[preflight] Dify administrator records: $accountCount"

$tenantCount = (Invoke-WslBash "docker exec $PostgresContainer psql -U postgres -d dify -At -c 'SELECT count(*) FROM tenants'")[0]
$parsedTenantCount = 0
if (-not [int]::TryParse($tenantCount, [ref]$parsedTenantCount) -or $parsedTenantCount -lt 1) {
    throw "Dify database exists, but tenants contains no tenant record. Administrator initialization is incomplete."
}
Write-Host "[preflight] Dify tenant records: $tenantCount"

$apiContainer = "dify-api-1"
$apiInfo = (((Invoke-WslBash "docker inspect $apiContainer") -join [Environment]::NewLine) | ConvertFrom-Json)[0]
$apiStorage = $apiInfo.Mounts | Where-Object Destination -eq "/app/api/storage"
if ($apiStorage.Type -ne "volume" -or $apiStorage.Name -ne $ExpectedAppStorageVolume) {
    throw "API storage is not using the fixed named volume '$ExpectedAppStorageVolume'."
}
Write-Host "[preflight] API storage volume: $ExpectedAppStorageVolume"

Invoke-WslBash "docker exec $apiContainer test -w /app/api/storage" | Out-Null
Write-Host "[preflight] API storage writable: PASS"

$pluginDaemonContainer = "dify-plugin_daemon-1"
$daemonBefore = (((Invoke-WslBash "docker inspect $pluginDaemonContainer") -join [Environment]::NewLine) | ConvertFrom-Json)[0]
if ($daemonBefore.State.Status -ne "running" -or $daemonBefore.State.Restarting) {
    throw "Plugin daemon is not stably running (status=$($daemonBefore.State.Status), restarting=$($daemonBefore.State.Restarting))."
}
$restartCountBefore = [int]$daemonBefore.RestartCount
Start-Sleep -Seconds 5
$daemonAfter = (((Invoke-WslBash "docker inspect $pluginDaemonContainer") -join [Environment]::NewLine) | ConvertFrom-Json)[0]
$restartCountAfter = [int]$daemonAfter.RestartCount
if ($daemonAfter.State.Status -ne "running" -or $daemonAfter.State.Restarting -or $restartCountAfter -ne $restartCountBefore) {
    throw "Plugin daemon restart loop detected (before=$restartCountBefore, after=$restartCountAfter, status=$($daemonAfter.State.Status))."
}
Write-Host "[preflight] Plugin daemon stable (restart count: $restartCountAfter): PASS"

function Invoke-ConsoleGetWithRetry {
    param([Parameter(Mandatory)][string]$Uri)

    $deadline = (Get-Date).AddSeconds(60)
    do {
        try {
            return Invoke-RestMethod -Uri $Uri -Method Get -TimeoutSec 10
        }
        catch {
            if ((Get-Date) -ge $deadline) { throw }
            Start-Sleep -Seconds 3
        }
    } while ($true)
}

$ping = Invoke-ConsoleGetWithRetry "http://localhost/console/api/ping"
if (-not $ping) {
    throw "Dify Console ping returned an empty response."
}
Write-Host "[preflight] Dify Console ping: PASS"

$setup = Invoke-ConsoleGetWithRetry "http://localhost/console/api/setup"
if ($setup.step -ne "finished") {
    throw "Dify Console setup is not finished (step=$($setup.step))."
}
Write-Host "[preflight] Dify Console setup finished: PASS"

Write-Host "[preflight] PASS - unique Compose project, fixed PostgreSQL data path, initialized Console data, storage permissions, required databases, and plugin daemon stability verified."

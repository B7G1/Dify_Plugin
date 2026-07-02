[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Label,
    [Parameter(Mandatory)][string]$OutputPath
)

$ErrorActionPreference = "Stop"
$postgres = "dify-db_postgres-1"
$daemon = "dify-plugin_daemon-1"

function Invoke-DockerText {
    param([Parameter(Mandatory)][string[]]$Arguments)
    $result = & docker @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($result -join [Environment]::NewLine) }
    return (($result -join [Environment]::NewLine).Trim())
}

$systemIdentifier = Invoke-DockerText @("exec", $postgres, "psql", "-U", "postgres", "-At", "-c", "select system_identifier from pg_control_system()")
$consoleCounts = (Invoke-DockerText @("exec", $postgres, "psql", "-U", "postgres", "-d", "dify", "-At", "-c", "select (select count(*) from accounts),(select count(*) from tenants)")) -split '\|'
$pluginCounts = (Invoke-DockerText @("exec", $postgres, "psql", "-U", "postgres", "-d", "dify_plugin", "-At", "-c", "select (select count(*) from plugins),(select count(*) from plugin_installations)")) -split '\|'
$pluginDatabase = Invoke-DockerText @("exec", $postgres, "psql", "-U", "postgres", "-At", "-c", "select exists(select 1 from pg_database where datname='dify_plugin')")
$daemonFields = (Invoke-DockerText @("inspect", $daemon, "--format", "{{.State.Status}}|{{.State.Restarting}}|{{.RestartCount}}")) -split '\|'
$postgresInspect = (Invoke-DockerText @("inspect", $postgres) | ConvertFrom-Json)[0]
$postgresMountInfo = $postgresInspect.Mounts | Where-Object Destination -eq "/var/lib/postgresql/data"
$postgresMount = "$($postgresMountInfo.Type)|$($postgresMountInfo.Name)"

$state = [ordered]@{
    label = $Label
    captured_at = (Get-Date).ToString("o")
    system_identifier = $systemIdentifier
    accounts = [int]$consoleCounts[0]
    tenants = [int]$consoleCounts[1]
    plugins = [int]$pluginCounts[0]
    plugin_installations = [int]$pluginCounts[1]
    dify_plugin_exists = ($pluginDatabase -eq "t")
    plugin_daemon = [ordered]@{
        status = $daemonFields[0]
        restarting = [bool]::Parse($daemonFields[1])
        restart_count = [int]$daemonFields[2]
    }
    postgres_mount = $postgresMount
}

$state | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $OutputPath -Encoding utf8
$state | ConvertTo-Json -Depth 4

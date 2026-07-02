param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$OutputPath = "..\reports\verification\$((Get-Date).ToString('yyyy-MM-dd'))\workflow_result.json"
)

$ErrorActionPreference = "Stop"
if (-not $env:DIFY_WORKFLOW_API_URL -or -not $env:DIFY_WORKFLOW_API_KEY) {
    throw "DIFY_WORKFLOW_API_URL and DIFY_WORKFLOW_API_KEY are required. Workflow verification does not skip."
}
$PluginRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PluginRoot
& $PythonExe ".\verification\verification_runner.py" workflow --output $OutputPath
if ($LASTEXITCODE -ne 0) { throw "Workflow verification failed: $OutputPath" }

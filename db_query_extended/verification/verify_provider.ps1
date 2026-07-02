param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$OutputPath = "..\reports\verification\$((Get-Date).ToString('yyyy-MM-dd'))\provider_result.json"
)

$ErrorActionPreference = "Stop"
$PluginRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PluginRoot
& $PythonExe ".\verification\verification_runner.py" provider --output $OutputPath
if ($LASTEXITCODE -ne 0) { throw "Provider verification failed: $OutputPath" }

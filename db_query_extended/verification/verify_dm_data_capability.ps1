param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$OutputPath = "..\reports\verification\$((Get-Date).ToString('yyyy-MM-dd'))\dm8_data_capability_closure\evidence.json"
)

$ErrorActionPreference = "Stop"
$PluginRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PluginRoot
& $PythonExe ".\verification\dm8_data_capability_runner.py" --output $OutputPath
if ($LASTEXITCODE -ne 0) { throw "DM8 data capability evidence failed: $OutputPath" }

param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$OutputPath = "..\reports\verification\$((Get-Date).ToString('yyyy-MM-dd'))\tool_result.json"
)

$ErrorActionPreference = "Stop"
$PluginRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PluginRoot
& $PythonExe ".\verification\verification_runner.py" tool --output $OutputPath
if ($LASTEXITCODE -ne 0) { throw "Tool verification failed: $OutputPath" }

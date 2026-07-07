param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$OutputPath = "..\reports\verification\$((Get-Date).ToString('yyyy-MM-dd'))\kingbasees_mock_result.json"
)

$ErrorActionPreference = "Stop"
$PluginRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PluginRoot

& $PythonExe ".\verification\kingbase_mock_runner.py" --output $OutputPath
if ($LASTEXITCODE -ne 0) {
    throw "KingbaseES mock verification failed: $OutputPath"
}

Write-Host "[kingbasees-mock] MOCK PASS; real database acceptance remains BLOCKED."


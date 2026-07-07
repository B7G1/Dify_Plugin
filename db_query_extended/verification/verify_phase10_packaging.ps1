param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$OutputPath = "..\reports\verification\$((Get-Date).ToString('yyyy-MM-dd'))\phase10_kingbasees\packaging_readiness.json"
)

$ErrorActionPreference = "Stop"
$PluginRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PluginRoot

& $PythonExe ".\verification\packaging_readiness_runner.py" --output $OutputPath
if ($LASTEXITCODE -ne 0) {
    throw "Phase 10 packaging readiness audit failed: $OutputPath"
}

$report = Get-Content -Raw -Encoding UTF8 $OutputPath | ConvertFrom-Json
Write-Host "[phase10-packaging] PASS=$($report.summary.pass) FAIL=$($report.summary.fail) SKIP=$($report.summary.skip) BLOCKED=$($report.summary.blocked)"
Write-Host "[phase10-packaging] Decision=$($report.decision); no package was built."


param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$OutputDir = "..\reports\verification\$((Get-Date).ToString('yyyy-MM-dd'))"
)

$ErrorActionPreference = "Stop"
$PluginRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PluginRoot
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

& ".\verification\verify_provider.ps1" -PythonExe $PythonExe -OutputPath "$OutputDir\provider_result.json"
& ".\verification\verify_tool.ps1" -PythonExe $PythonExe -OutputPath "$OutputDir\tool_result.json"
& ".\verification\verify_workflow.ps1" -PythonExe $PythonExe -OutputPath "$OutputDir\workflow_result.json"

$suiteFiles = @("provider_result.json", "tool_result.json", "workflow_result.json")
$summary = [ordered]@{
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    suites = @()
    summary = [ordered]@{ pass = 0; fail = 0; skip = 0 }
}
foreach ($file in $suiteFiles) {
    $suite = Get-Content -Raw -Encoding UTF8 (Join-Path $OutputDir $file) | ConvertFrom-Json
    $summary.suites += [ordered]@{ name = $suite.suite; report = $file; summary = $suite.summary }
    $summary.summary.pass += $suite.summary.pass
    $summary.summary.fail += $suite.summary.fail
    $summary.summary.skip += $suite.summary.skip
}
$summary | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $OutputDir "summary.json")
$summary.summary | Format-List
if ($summary.summary.fail -ne 0 -or $summary.summary.skip -ne 0) {
    throw "Full verification requires FAIL=0 and SKIP=0. See $OutputDir\summary.json"
}
Write-Host "[verify_all] PASS - reports written to $OutputDir"

param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$OutputDir = "..\reports\verification\$((Get-Date).ToString('yyyy-MM-dd'))\phase10_kingbasees",
    [switch]$RunV1Regression
)

$ErrorActionPreference = "Stop"
$PluginRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PluginRoot
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$mockPath = Join-Path $OutputDir "mock_result.json"
& ".\verification\verify_kingbase_mock.ps1" -PythonExe $PythonExe -OutputPath $mockPath

$requiredRealVariables = @(
    "KINGBASE_HOST",
    "KINGBASE_DATABASE",
    "KINGBASE_USERNAME",
    "KINGBASE_PASSWORD"
)
$missing = @($requiredRealVariables | Where-Object { -not [Environment]::GetEnvironmentVariable($_) })
$realStatus = $null
if ($missing.Count -eq 0) {
    $WorkspaceRoot = Split-Path -Parent $PluginRoot
    $probePath = Join-Path $WorkspaceRoot "reports\documentation\Phase10_KingbaseES_Adapter\driver_feasibility_probe.py"
    $probeOutput = & $PythonExe $probePath
    $probeExit = $LASTEXITCODE
    try {
        $realStatus = $probeOutput | ConvertFrom-Json
    } catch {
        $realStatus = [ordered]@{
            status = "FAIL"
            reason = "Driver feasibility probe did not return valid JSON."
            executed = $true
        }
    }
    if ($probeExit -ne 0 -and $realStatus.status -eq "PASS") {
        $realStatus.status = "FAIL"
    }
} else {
    $realStatus = [ordered]@{
        status = "BLOCKED"
        reason = "Real KingbaseES server, approved driver/runtime, and credentials are required."
        missing_environment = $missing
        executed = $false
    }
}
$realStatus | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $OutputDir "real_status.json")

$baselineStatus = [ordered]@{
    status = "NOT_RUN"
    required = "45 PASS / 0 FAIL / 0 SKIP"
    reason = "Use -RunV1Regression with the existing Workflow API environment variables."
}
if ($RunV1Regression) {
    if (-not $env:DIFY_WORKFLOW_API_URL -or -not $env:DIFY_WORKFLOW_API_KEY) {
        $baselineStatus.status = "BLOCKED"
        $baselineStatus.reason = "DIFY_WORKFLOW_API_URL and DIFY_WORKFLOW_API_KEY are required for the untouched v1 regression."
    } else {
        $baselineDir = Join-Path $OutputDir "v1_regression"
        & ".\verification\verify_all.ps1" -PythonExe $PythonExe -OutputDir $baselineDir
        $baselineStatus = Get-Content -Raw -Encoding UTF8 (Join-Path $baselineDir "summary.json") | ConvertFrom-Json
    }
}
$baselineStatus | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $OutputDir "v1_regression_status.json")

$mock = Get-Content -Raw -Encoding UTF8 $mockPath | ConvertFrom-Json
$summary = [ordered]@{
    phase = "Phase 10 KingbaseES"
    evidence_level = "MOCK_ONLY"
    mock = $mock.summary
    real_database = $realStatus.status
    workflow = "BLOCKED"
    api = "BLOCKED"
    v1_regression = $baselineStatus
    final_acceptance = "BLOCKED"
}
$summary | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $OutputDir "summary.json")
$summary | Format-List

if ($mock.summary.fail -ne 0) {
    throw "Phase 10 mock verification has failures."
}
Write-Host "[phase10] MOCK checks completed; all real KingbaseES acceptance remains BLOCKED."

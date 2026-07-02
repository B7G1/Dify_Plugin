param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$ReportPath = ".\verification\phase2_verification_report.json"
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$PluginRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PluginRoot

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

if (-not (Test-Path ".\verification")) {
    New-Item -ItemType Directory -Path ".\verification" | Out-Null
}

Write-Host "[Phase2] Running db_query_extended plugin verification matrix..."
$json = & $PythonExe ".\verification\phase2_matrix.py"
$exitCode = $LASTEXITCODE
$json | Out-File -FilePath $ReportPath -Encoding utf8

Write-Host "[Phase2] Verification report written to $ReportPath"
$report = Get-Content -LiteralPath $ReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
$report.summary | Format-List

if ($exitCode -ne 0) {
    throw "Phase2 verification failed. See $ReportPath"
}

Write-Host "[Phase2] PASS"

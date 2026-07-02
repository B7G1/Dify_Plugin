[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][string]$EvidenceDirectory,
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'reports\generated'),
    [string]$ReleaseVersion = 'v1.0'
)

$ErrorActionPreference = 'Stop'
$SummaryPath = Join-Path $EvidenceDirectory 'summary.json'
if (-not (Test-Path -LiteralPath $SummaryPath)) {
    throw "Missing verification summary: $SummaryPath"
}

$summaryDocument = Get-Content -LiteralPath $SummaryPath -Raw | ConvertFrom-Json
$total = $summaryDocument.summary
foreach ($name in @('pass', 'fail', 'skip')) {
    if ($null -eq $total.$name) { throw "summary.json is missing summary.$name" }
}

$generatedAt = Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'
$status = if (($total.fail -eq 0) -and ($total.skip -eq 0)) { 'PASS' } else { 'NOT PASS' }
$technical = @"
# Technical Report — $ReleaseVersion

Generated: $generatedAt

- Verification: **$status**
- PASS: $($total.pass)
- FAIL: $($total.fail)
- SKIP: $($total.skip)

Source: $SummaryPath
"@
$executive = @"
# Executive Report — $ReleaseVersion

The automated verification status is **$status**: $($total.pass) passed, $($total.fail) failed, and $($total.skip) skipped.

This generated summary contains no credentials. Release approval remains a human decision.
"@
$verification = @"
# Verification Report — $ReleaseVersion

| Result | Count |
| --- | ---: |
| PASS | $($total.pass) |
| FAIL | $($total.fail) |
| SKIP | $($total.skip) |

Authoritative input: $SummaryPath
"@
$releaseNotes = @"
# Generated Release Notes — $ReleaseVersion

Automated acceptance: **$($total.pass) PASS / $($total.fail) FAIL / $($total.skip) SKIP**.

Merge this factual section into the curated release notes; do not overwrite limitations, compatibility, or migration guidance.
"@
$dashboard = @"
<!doctype html><html><head><meta charset="utf-8"><title>$ReleaseVersion verification</title><style>body{font:16px system-ui;max-width:760px;margin:40px auto}.ok{color:#08783e}</style></head><body><h1>$ReleaseVersion Verification</h1><p class="ok"><strong>$($total.pass) PASS / $($total.fail) FAIL / $($total.skip) SKIP</strong></p><p>Generated $generatedAt from machine-readable evidence.</p></body></html>
"@

$outputs = [ordered]@{
    'Technical_Report.md' = $technical
    'Executive_Report.md' = $executive
    'Verification_Report.md' = $verification
    'Release_Notes.generated.md' = $releaseNotes
    'dashboard.generated.html' = $dashboard
}

if ($PSCmdlet.ShouldProcess($OutputDirectory, 'Generate reports from verified JSON')) {
    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    foreach ($entry in $outputs.GetEnumerator()) {
        Set-Content -LiteralPath (Join-Path $OutputDirectory $entry.Key) -Value $entry.Value -Encoding utf8
    }
}

$outputs.Keys | ForEach-Object { Join-Path $OutputDirectory $_ }

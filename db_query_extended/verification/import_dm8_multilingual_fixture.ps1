param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe",
    [string]$SqlPath = "E:\Dify_Plugin\local_test_db\dm8\04_multilingual_fixture.sql",
    [string]$OutputPath = "E:\Dify_Plugin\reports\verification\$((Get-Date).ToString('yyyy-MM-dd'))\dm8_multilingual_fixture_import_result.json"
)

$ErrorActionPreference = "Stop"
$PluginRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PluginRoot

if (-not $env:DM_ADMIN_HOST) { $env:DM_ADMIN_HOST = "127.0.0.1" }
if (-not $env:DM_ADMIN_PORT) { $env:DM_ADMIN_PORT = "5236" }
if (-not $env:DM_ADMIN_DATABASE) { $env:DM_ADMIN_DATABASE = "DMSERVER" }
if (-not $env:DM_ADMIN_USERNAME) { $env:DM_ADMIN_USERNAME = "PLUGIN_TEST_OWNER" }

if (-not $env:DM_ADMIN_PASSWORD) {
    $securePassword = Read-Host "DM8 admin/owner password for $($env:DM_ADMIN_USERNAME)" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    try {
        $env:DM_ADMIN_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

& $PythonExe ".\verification\import_dm8_multilingual_fixture.py" --sql $SqlPath --output $OutputPath
if ($LASTEXITCODE -ne 0) { throw "DM8 multilingual fixture import failed: $OutputPath" }

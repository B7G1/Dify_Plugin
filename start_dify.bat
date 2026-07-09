@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "START_SCRIPT=%SCRIPT_DIR%db_query_extended\verification\start_dify.ps1"

if not exist "%START_SCRIPT%" (
  echo [ERROR] Dify startup script not found:
  echo %START_SCRIPT%
  pause
  exit /b 1
)

echo [start_dify] Starting Dify through the fixed baseline launcher...
powershell -NoProfile -ExecutionPolicy Bypass -File "%START_SCRIPT%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo.
  echo [ERROR] Dify startup failed. Exit code: %EXIT_CODE%
  pause
  exit /b %EXIT_CODE%
)

echo.
echo [start_dify] Done. Open http://localhost
pause
